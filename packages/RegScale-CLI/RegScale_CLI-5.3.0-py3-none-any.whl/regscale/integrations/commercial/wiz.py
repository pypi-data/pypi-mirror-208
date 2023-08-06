#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates Wiz.io into RegScale"""

# standard python imports
import codecs
import csv
import dataclasses
import datetime
import io
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, wait
from contextlib import closing
from datetime import date
from os import mkdir, path, sep
from typing import Tuple

import click
import pandas as pd
import requests
from rich.progress import track

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    capitalize_words,
    check_config_for_issues,
    check_file_path,
    check_license,
    convert_datetime_to_regscale_string,
    create_progress_object,
    find_uuid_in_str,
    format_dict_to_html,
    get_current_datetime,
    get_env_variable,
    recursive_items,
)
from regscale.core.app.utils.regscale_utils import (
    Modules,
    error_and_exit,
    verify_provided_module,
)
from regscale.models import regscale_id, regscale_module
from regscale.models.integration_models.wiz import AssetCategory
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue

# TODO:
# Compute resources from Wiz to default.


# Pull Wiz secret and ID from environment and not from plaintext


# Private and global variables
logger = create_logger()
job_progress = create_progress_object()
url_job_progress = create_progress_object()
regscale_job_progress = create_progress_object()

AUTH0_URLS = [
    "https://auth.wiz.io/oauth/token",
    "https://auth0.gov.wiz.io/oauth/token",
    "https://auth0.test.wiz.io/oauth/token",
    "https://auth0.demo.wiz.io/oauth/token",
]
COGNITO_URLS = [
    "https://auth.app.wiz.io/oauth/token",
    "https://auth.gov.wiz.io/oauth/token",
    "https://auth.test.wiz.io/oauth/token",
    "https://auth.demo.wiz.io/oauth/token",
]

CHECK_INTERVAL_FOR_DOWNLOAD_REPORT = 7
MAX_RETRIES = 100

CREATE_REPORT_QUERY = """
    mutation CreateReport($input: CreateReportInput!) {
    createReport(input: $input) {
        report {
        id
        }
    }
    }
"""

# TODO: Use RegScale properties for Wiz
# TODO: issue mappings


# Create group to handle Wiz.io integration
@click.group()
def wiz():
    """Integrates continuous monitoring data from Wiz.io."""


@wiz.command()
@click.option("--client_id", default=None, hide_input=False, required=False)
@click.option("--client_secret", default=None, hide_input=True, required=False)
def authenticate(client_id, client_secret):
    """Authenticate to Wiz."""
    wiz_authenticate(client_id, client_secret)


def wiz_authenticate(client_id: str = None, client_secret: str = None) -> None:
    """
    Authenticate to Wiz
    :param str client_id: Wiz client ID, defaults to None
    :param str client_secret: Wiz client secret, defaults to None
    :return: None
    """
    app = check_license()
    api = Api(app)
    # Login with service account to retrieve a 24 hour access token that updates YAML file
    logger.info("Authenticating - Loading configuration from init.yaml file")

    # load the config from YAML
    config = app.config

    # get secrets
    if "wizclientid" in [key.lower() for key in os.environ] and not client_id:
        client_id = get_env_variable("WizClientID")
    if not client_id:
        raise ValueError(
            "No Wiz Client ID provided in system environment or CLI command."
        )
    if "wizclientsecret" in [key.lower() for key in os.environ] and not client_secret:
        client_secret = get_env_variable("WizClientSecret")
    if not client_secret:
        raise ValueError(
            "No Wiz Client Secret provided in system environment or CLI command."
        )
    if "wizAuthUrl" in config:
        wiz_auth_url = config["wizAuthUrl"]
    else:
        error_and_exit("No Wiz Authentication URL provided in the init.yaml file.")

    # login and get token
    logger.info("Attempting to retrieve OAuth token from Wiz.io.")
    token, scope = get_token(
        api=api,
        client_id=client_id,
        client_secret=client_secret,
        token_url=wiz_auth_url,
    )

    # assign values

    config["wizAccessToken"] = token
    config["wizScope"] = scope

    # write our the result to YAML
    # write the changes back to file
    app.save_config(config)


def get_token(
    api: Api, client_id: str, client_secret: str, token_url: str
) -> tuple[str, str]:
    """
    Return Wiz.io token
    :param Api api: api instance
    :param str client_id: Wiz client ID
    :param str client_secret: Wiz client secret
    :param str token_url: token url
    :return: tuple of token and scope
    :rtype: tuple[str, str]
    """
    logger.info("Getting a token")
    response = api.post(
        url=token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        json=None,
        data=generate_authentication_params(client_id, client_secret, token_url),
    )
    logger.debug(response.reason)
    if response.status_code == requests.codes.unauthorized:
        error_and_exit("Wiz Authentication: Unauthorized")
    if response.status_code != requests.codes.ok:
        error_and_exit(
            f"Error authenticating to Wiz [{response.status_code}] - {response.text}"
        )
    response_json = response.json()
    token = response_json.get("access_token")
    scope = response_json.get("scope")
    if not token:
        error_and_exit(
            f'Could not retrieve token from Wiz: {response_json.get("message")}'
        )
    logger.info("SUCCESS: Wiz.io access token successfully retrieved.")
    return token, scope


def generate_authentication_params(
    client_id: str, client_secret: str, token_url: str
) -> dict:
    """
    Create the Correct Parameter format based on URL
    :param str client_id: Wiz Client ID
    :param str client_secret: Wiz Client Secret
    :param str token_url: Wiz URL
    :raises Exception: A generic exception if token_url provided is invalid
    :return: Dictionary containing authentication parameters
    :rtype: dict
    """
    if token_url in AUTH0_URLS:
        return {
            "grant_type": "client_credentials",
            "audience": "beyond-api",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    if token_url in COGNITO_URLS:
        return {
            "grant_type": "client_credentials",
            "audience": "wiz-api",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    error_and_exit("Invalid Token URL")


@wiz.command()
@click.option(
    "--wiz_project_id",
    prompt="Enter the Wiz project ID",
    help="Enter the Wiz Project ID.  Options include: projects, \
          policies, supplychain, securityplans, components.",
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option("--client_id", default=None, hide_input=False, required=False)
@click.option("--client_secret", default=None, hide_input=True, required=False)
def inventory(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
) -> None:
    """Wrapper to process inventory list from Wiz.

    :param wiz_project_id: A Wiz project ID
    :param regscale_id: RegScale ID
    :param regscale_module: RegScale module
    :param client_id: Wiz Client ID
    :param client_secret: Wiz Client Secret
    :rType: None
    """
    fetch_inventory(
        wiz_project_id=wiz_project_id,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        client_id=client_id,
        client_secret=client_secret,
    )


def fetch_inventory(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
) -> None:
    """Process inventory list from Wiz.

    :param wiz_project_id: A Wiz project ID
    :param regscale_id: RegScale ID
    :param regscale_module: RegScale module
    :param client_id: Wiz Client ID
    :param client_secret: Wiz Client Secret
    :rType: None
    """
    wiz_authenticate(client_id, client_secret)
    app = check_license()
    api = Api(app)
    verify_provided_module(regscale_module)
    # load the config from YAML
    config = app.config
    if not check_module_id(app, regscale_id, regscale_module):
        error_and_exit(f"Please enter a valid regscale_id for {regscale_module}.")

    # get secrets
    url = config["wizUrl"]

    # get the full list of assets
    logger.info("Fetching full asset list from RegScale.")

    try:
        body = """
                query {
                    assets(take: 50, skip: 0, , where: { parentModule: {eq: "parent_module"} parentId: {
                      eq: parent_id
                    }}) {
                    items {
                        id
                        name
                        parentId
                        wizId
                        parentModule
                        ipAddress
                        macAddress
                        description
                        notes
                    },
                    pageInfo {
                        hasNextPage
                    }
                    ,totalCount 
                    }
                }
                    """.replace(
            "parent_module", regscale_module
        ).replace(
            "parent_id", str(regscale_id)
        )

        existing_asset_data = api.graph(query=body)["assets"]["items"]

    except requests.RequestException as ex:
        error_and_exit(f"ERROR: Unable to retrieve asset list from RegScale.\n {ex}")

    # make directory if it doesn't exist
    if path.exists("artifacts") is False:
        mkdir("artifacts")
        logger.warning(
            "Artifacts directory does not exist.  Creating new directory for artifact \
                processing."
        )

    else:
        logger.info(
            "Artifacts directory exists.  This directly will store output files from all processing."
        )

    report_prefix = f"RegScale_Inventory_Report_Automated_Entities_{wiz_project_id}"
    existing_inventory_reports = [
        report for report in query_reports(app) if report_prefix in report["name"]
    ]
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    # Update existing reports
    for report in existing_inventory_reports:
        last_run = datetime.datetime.strptime(
            report["lastRun"]["runAt"], date_format
        )  # UTC
        if (
            (datetime.datetime.utcnow() - last_run).seconds
            > (app.config["wizReportAge"]) * 60
            if app.config["wizReportAge"] != 0
            else 1
        ):  # Rerun old reports
            rerun_report(app, report["id"])

    # Update Existing reports, if any

    # if report ids are null, create
    wiz_report_ids = create_or_update_inventory_report(
        app,
        url,
        existing_inventory_reports,
        report_prefix=report_prefix,
        wiz_project_id=wiz_project_id,
    )
    properties, wiz_assets = create_assets(
        app,
        wiz_report_ids,
        parent_id=regscale_id,
        parent_module=regscale_module,
    )
    new_assets = [
        asset
        for asset in wiz_assets
        if asset["wizId"] not in {wiz["wizId"] for wiz in existing_asset_data}
    ]
    update_assets = []
    existing_wiz_ids = {wiz["wizId"] for wiz in existing_asset_data}
    for asset in existing_asset_data:
        if asset["wizId"] in existing_wiz_ids:
            regscale_id = asset["id"]
            if wiz_index := next(
                (
                    index
                    for (index, d) in enumerate(wiz_assets)
                    if d["wizId"] == asset["wizId"]
                ),
                None,
            ):
                update_asset = wiz_assets[wiz_index]
                update_asset["id"] = regscale_id
                if Asset.from_dict(update_asset) != Asset.from_dict(asset):
                    update_assets.append(update_asset)

    api.update_server(
        config=app.config,
        url=app.config["domain"] + "/api/assets",
        method="put",
        message=f"[#6200ff]Updating {len(update_assets)} assets in RegScale.",
        json_list=update_assets,
    )
    new_props = []
    for asset in track(
        new_assets,
        description=f"[#ba1d49]Inserting {len(new_assets)} new assets in RegScale.",
    ):
        response = api.post(url=app.config["domain"] + "/api/assets", json=asset)
        asset_id = None
        if not response.raise_for_status():
            asset_id = response.json()["id"]
            for prop in properties:
                # Update property records with a valid parent id from the newly inserted asset.
                if prop["wiz_id"] == response.json()["wizId"]:
                    prop["parentId"] = asset_id
                    new_props.append(prop)
    if new_props:
        # Batch post new properties.
        api.post(
            url=app.config["domain"] + "/api/properties/batchcreate",
            json=new_props,
        )


def create_assets(
    app: Application,
    wiz_report_ids: list[str],
    parent_id: int,
    parent_module: str,
) -> tuple[list[dict], list[Asset]]:
    """
    Create Wiz Assets and Sync to RegScale
    :param Application app: The application instance
    :param list wiz_report_ids: A list of Wiz report IDs
    :param int parent_id: ID from RegScale of parent
    :param str parent_module: Parent Module of item in RegScale
    :raises Exception: A generic exception
    :raises requests.RequestException: A requests exception
    :return: properties: str, wiz_assets: list
    :rtype: tuple[list[dict], list[Asset]]
    """
    frames = []
    properties = None

    def gather_urls(report_id: str) -> list[str]:
        """Gather download URLS for wiz reports

        :param wiz_report_ids: A list of report ids
        :return: A list of urls.
        """
        download_url = get_report_url_and_status(app=app, report_id=report_id)
        url_job_progress.update(gathering_urls, advance=1)
        return download_url

    def stream_inventory(args: Tuple) -> None:
        (url, session) = args
        # find which records should be executed by the current thread
        logger.debug("Downloading %s", url)
        response = session.get(url, stream=True)
        url_data = response.content
        stream_frame = pd.read_csv(io.StringIO(url_data.decode("utf-8")))
        logger.debug(len(stream_frame))
        frames.append(stream_frame)
        job_progress.update(downloading_reports, advance=1)
        logger.debug("Frame Update.. for %s", url)

    mapping = {
        "ACCESS_ROLE": "Other",
        "ACCESS_ROLE_BINDING": "Other",
        "ACCESS_ROLE_PERMISSION": "Other",
        "API_GATEWAY": "Other",
        "APPLICATION": "Other",
        "AUTHENTICATION_CONFIGURATION": "Other",
        "BACKUP_SERVICE": "Other",
        "BUCKET": "Other",
        "CDN": "Other",
        "CERTIFICATE": "Other",
        "CICD_SERVICE": "Other",
        "CLOUD_LOG_CONFIGURATION": "Other",
        "CLOUD_ORGANIZATION": "Other",
        "COMPUTE_INSTANCE_GROUP": "Other",
        "CONFIG_MAP": "Other",
        "CONTAINER": "Other",
        "CONTAINER_GROUP": "Other",
        "CONTAINER_IMAGE": "Other",
        "CONTAINER_REGISTRY": "Other",
        "CONTAINER_SERVICE": "Other",
        "DAEMON_SET": "Other",
        "DATABASE": "Other",
        "DATA_WORKLOAD": "Other",
        "DB_SERVER": "Physical Server",
        "DEPLOYMENT": "Other",
        "DNS_RECORD": "Other",
        "DNS_ZONE": "Other",
        "DOMAIN": "Other",
        "EMAIL_SERVICE": "Other",
        "ENCRYPTION_KEY": "Other",
        "ENDPOINT": "Other",
        "FILE_SYSTEM_SERVICE": "Other",
        "FIREWALL": "Firewall",
        "GATEWAY": "Other",
        "GOVERNANCE_POLICY": "Other",
        "GOVERNANCE_POLICY_GROUP": "Other",
        "HOSTED_APPLICATION": "Other",
        "IAM_BINDING": "Other",
        "IP_RANGE": "Other",
        "KUBERNETES_CLUSTER": "Other",
        "KUBERNETES_CRON_JOB": "Other",
        "KUBERNETES_INGRESS": "Other",
        "KUBERNETES_INGRESS_CONTROLLER": "Other",
        "KUBERNETES_JOB": "Other",
        "KUBERNETES_NETWORK_POLICY": "Other",
        "KUBERNETES_NODE": "Other",
        "KUBERNETES_PERSISTENT_VOLUME": "Other",
        "KUBERNETES_PERSISTENT_VOLUME_CLAIM": "Other",
        "KUBERNETES_POD_SECURITY_POLICY": "Other",
        "KUBERNETES_SERVICE": "Other",
        "KUBERNETES_STORAGE_CLASS": "Other",
        "KUBERNETES_VOLUME": "Other",
        "LOAD_BALANCER": "Other",
        "MANAGED_CERTIFICATE": "Other",
        "MANAGEMENT_SERVICE": "Other",
        "NETWORK_ADDRESS": "Other",
        "NETWORK_INTERFACE": "Other",
        "NETWORK_ROUTING_RULE": "Other",
        "NETWORK_SECURITY_RULE": "Other",
        "PEERING": "Other",
        "POD": "Other",
        "PORT_RANGE": "Other",
        "PRIVATE_ENDPOINT": "Other",
        "PROXY": "Other",
        "PROXY_RULE": "Other",
        "RAW_ACCESS_POLICY": "Other",
        "REGISTERED_DOMAIN": "Other",
        "REPLICA_SET": "Other",
        "RESOURCE_GROUP": "Other",
        "SEARCH_INDEX": "Other",
        "SUBNET": "Other",
        "SUBSCRIPTION": "Other",
        "SWITCH": "Network Switch",
        "VIRTUAL_DESKTOP": "Virtual Machine (VM)",
        "VIRTUAL_MACHINE": "Virtual Machine (VM)",
        "VIRTUAL_MACHINE_IMAGE": "Other",
        "VIRTUAL_NETWORK": "Other",
        "VOLUME": "Other",
        "WEB_SERVICE": "Other",
        "DATA_WORKFLOW": "Other",
    }
    api = Api(app)
    random.shuffle(wiz_report_ids)
    wiz_assets = []
    logger.info("Streaming Automated Inventory Report(s) to RegScale Assets..")
    session = api.session
    urls = []
    with url_job_progress:
        gathering_urls = url_job_progress.add_task(
            f"[#ba1d49]Gathering {len(wiz_report_ids)} Wiz report URL(s)...",
            total=len(wiz_report_ids),
        )
        n_threads = (
            int(len(wiz_report_ids) / 4) if int(len(wiz_report_ids) / 4) != 0 else 4
        )
        with ThreadPoolExecutor(n_threads) as url_executor:
            # download each url and save as a local file
            url_futures = [
                url_executor.submit(gather_urls, report_id)
                for report_id in wiz_report_ids
            ]
            # wait for all download tasks to complete
            _, _ = wait(url_futures)
            urls = [result.result() for result in url_futures]

    if url_job_progress.finished:
        with job_progress:
            downloading_reports = job_progress.add_task(
                f"[#f68d1f]Downloading {len(urls)} Wiz inventory report(s)...",
                total=len(urls),
            )
            n_threads = len(urls)
            with ThreadPoolExecutor(
                int(n_threads / 8) if int(n_threads / 8) != 0 else 4
            ) as download_executor:  # Wiz download speeds might be throttled, going easy here.
                # download each url and save as a local file
                futures = [
                    download_executor.submit(stream_inventory, (url, session))
                    for url in urls
                ]
                # wait for all download tasks to complete
                _, _ = wait(futures)
    if job_progress.finished and frames:
        all_df = pd.concat(frames)
        logger.info("Merging reports to a dataset with %i records", len(all_df))
        for _, row in all_df.iterrows():
            if isinstance(row["Provider ID"], str):
                provider_id = (
                    find_uuid_in_str(row["Provider ID"])
                    if isinstance(row["Provider ID"], str)
                    else row["Provider ID"]
                )
                wiz_data = json.dumps(
                    {
                        "tags": json.loads(row["Tags"]),
                        "wiz_json": json.loads(row["Wiz JSON Object"]),
                        "other": json.loads(row["Cloud Native JSON"]),
                    }
                )
                properties = get_properties(
                    app=app, wiz_data=wiz_data, wiz_id=provider_id
                )
                external_id = row["External ID"]
                description = format_dict_to_html(
                    {
                        "Tags": json.loads(row["Tags"]),
                        "WizJSON": json.loads(row["Wiz JSON Object"]),
                        "CloudNativeJSON": json.loads(row["Cloud Native JSON"]),
                    }
                )
                r_asset = Asset(
                    name=row["Name"],
                    notes=f"External ID: {external_id}",
                    otherTrackingNumber=provider_id,
                    wizId=external_id,
                    wizInfo=None,
                    parentId=parent_id,
                    parentModule=parent_module,
                    ipAddress=None,
                    macAddress=None,
                    operatingSystem=row["app.kubernetes.io/os"]
                    if "app.kubernetes.io/os" in json.loads(row["Tags"]).keys()
                    else None,
                    assetOwnerId=app.config["userId"],
                    status="Active (On Network)",  # Get Status from Tags
                    assetCategory=map_category(row["Resource Type"]),
                    assetType=mapping[row["Resource Type"]]
                    if row["Resource Type"] in mapping
                    else "Other",
                    description=description,
                )
                wiz_assets.append(dataclasses.asdict(r_asset))
        logger.info(
            "%i Wiz Assets with valid provider id's filtered..",
            len(wiz_assets),
        )
    if len(wiz_assets) == 0:
        logger.warning("No Wiz Assets found!")
        sys.exit(0)
    return properties, wiz_assets


@wiz.command()
@click.option(
    "--wiz_project_id",
    prompt="Enter the project ID for Wiz",
    default=None,
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(
    "--issue_severity_filter",
    default="low, medium, high, critical",
    help="A filter for the severity types included in the wiz issues report. defaults to ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']",
    type=click.STRING,
    hide_input=False,
    required=False,
)
@click.option("--client_id", default=None, hide_input=False, required=False)
@click.option("--client_secret", default=None, hide_input=True, required=False)
# flake8: noqa: C901
def issues(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
    issue_severity_filter: str,
) -> None:
    """Wrapper to process Issues from Wiz.

    :param wiz_project_id: Wiz Project ID
    :param regscale_id: RegScale ID
    :param regscale_module: RegScale Module
    :param client_id: Wiz Client ID
    :param client_secret: Wiz Client Secret
    :param issue_severity_filter: Wiz Issue Severity Filter
    """
    process_wiz_issues(
        wiz_project_id=wiz_project_id,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        client_id=client_id,
        client_secret=client_secret,
        issue_severity_filter=issue_severity_filter,
    )


def process_wiz_issues(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
    issue_severity_filter: str,
) -> None:
    """Process Issues from Wiz.

    :param wiz_project_id: Wiz Project ID
    :param regscale_id: RegScale ID
    :param regscale_module: RegScale Module
    :param client_id: Wiz Client ID
    :param client_secret: Wiz Client Secret
    :param issue_severity_filter: Wiz Issue Severity Filter
    """
    # TODO: update wiz critical high low params
    # TODO: add filter object from wiz.
    issues_severity = [
        iss.upper().strip() for iss in issue_severity_filter.split(",")
    ]  # Case insensitive for the user.

    wiz_authenticate(client_id, client_secret)
    app = check_license()
    config = app.config
    api = Api(app)
    if not "wizIssuesReportId" in config:
        config["wizIssuesReportId"] = {}
        config["wizIssuesReportId"]["report_id"] = None
        config["wizIssuesReportId"]["last_seen"] = None
        app.save_config(config)
    verify_provided_module(regscale_module)
    wiz_report_info = None
    # load the config from YAML
    wiz_report_id = None
    if not check_module_id(app, regscale_id, regscale_module):
        error_and_exit(f"Please enter a valid regscale_id for {regscale_module}.")

    # get secrets
    url = config["wizUrl"]
    # set headers
    if regscale_module == "securityplans":
        existing_regscale_issues = Issue.fetch_issues_by_ssp(
            app=app, ssp_id=regscale_id
        )
    else:
        existing_regscale_issues = Issue.fetch_issues_by_parent(
            app=app, regscale_id=regscale_id, regscale_module=regscale_module
        )
    # Only pull issues that have a wizId
    existing_regscale_issues = [iss for iss in existing_regscale_issues if iss.wizId]
    check_file_path("artifacts")

    # write out issues data to file
    if len(existing_regscale_issues) > 0:
        with open(
            f"artifacts{sep}existingRecordIssues.json", "w", encoding="utf-8"
        ) as outfile:
            outfile.write(
                json.dumps(
                    [dataclasses.asdict(iss) for iss in existing_regscale_issues],
                    indent=4,
                )
            )
        logger.info(
            "Writing out RegScale issue list for Record # %s "
            "to the artifacts folder (see existingRecordIssues.json)",
            str(regscale_id),
        )
    logger.info(
        "%s existing issues retrieved for processing from RegScale.",
        str(len(existing_regscale_issues)),
    )
    issue_report_name = f"RegScale_Issues_Report_project_{wiz_project_id}_{'_'.join([fil.lower() for fil in issues_severity])}"
    rpts = [
        report for report in query_reports(app) if report["name"] == issue_report_name
    ]
    if rpts:
        last_seen = (
            app.config["wizIssuesReportId"]["last_seen"]
            if "wizIssuesReportId" in app.config
            and "last_seen" in app.config["wizIssuesReportId"].keys()
            else None
        )
        if not last_seen:
            rerun_report(app, rpts[0]["id"])
            last_seen = app.config["wizIssuesReportId"]["last_seen"]
        report_data = {
            "report_id": rpts[0]["id"],
            "last_seen": last_seen,
        }
        wiz_report_info = report_data
        app.config["wizIssuesReportId"] = wiz_report_info
        app.save_config(app.config)

    # find report if exists and is valid
    if "wizIssuesReportId" in app.config and wiz_report_id is None:
        try:
            assert app.config["wizIssuesReportId"]["report_id"] == rpts[0]["id"]
            date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            last_run = datetime.datetime.strptime(
                rpts[0]["lastRun"]["runAt"], date_format
            )  # UTC
            if (
                (datetime.datetime.utcnow() - last_run).seconds
                > (app.config["wizReportAge"]) * 60
                if app.config["wizReportAge"] != 0
                else 1
            ):  # Rerun old reports
                rerun_report(app, wiz_report_info["report_id"])

        except (AssertionError, IndexError):
            logger.warning(
                "Report not found, creating Automated RegScale report on Wiz"
            )
            wiz_report_id = create_issues_report(
                app,
                url,
                issue_report_name,
                wiz_project_id=wiz_project_id,
                issues_severity=issues_severity,
            )
    elif rpts:
        app.config["wizIssuesReportId"] = report_data
        wiz_report_id = app.config["wizIssuesReportId"]["report_id"]
        app.save_config(app.config)
    else:
        wiz_report_id = create_issues_report(
            app,
            url,
            issue_report_name,
            wiz_project_id=wiz_project_id,
            issues_severity=issues_severity,
        )
    wiz_report_id = wiz_report_info["report_id"] if wiz_report_info else wiz_report_id
    report_url = get_report_url_and_status(app=app, report_id=wiz_report_id)

    # Fetch the data!
    wiz_issues = fetch_wiz_issues(
        config=app.config,
        download_url=report_url,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
    )
    update_issues = []
    filtered_issues = [
        dataclasses.asdict(wiz)
        for wiz in wiz_issues
        if wiz["wizId"] not in set(reg["wizId"] for reg in existing_regscale_issues)
    ]
    new_issues = []
    fmt = "%Y-%m-%d %H:%M:%S"

    for issue in filtered_issues:
        days = 5
        if issue["severityLevel"] == "III - Low - Other Weakness":
            days = config["issues"]["wiz"]["low"]
        elif issue["severityLevel"] == "II - Moderate - Reportable Condition":
            days = config["issues"]["wiz"]["medium"]
        elif issue["severityLevel"] == "I - High - Other Weakness":
            days = config["issues"]["wiz"]["high"]
        else:
            days = config["issues"]["wiz"]["low"]
        issue["dueDate"] = (
            datetime.datetime.now() + datetime.timedelta(days=days)
        ).strftime(fmt)
        new_issues.append(issue)
    for issue in existing_regscale_issues:
        set_wiz_issues = set(wiz["wizId"] for wiz in wiz_issues)
        issue["status"] = "Open" if issue["wizId"] in set_wiz_issues else "Closed"
        issue["description"] = (
            issue["description"]
            if issue["wizId"] in set_wiz_issues
            else issue["description"]
        )
        # concatenate the new security check from wiz if RegScale issue is found in Wiz issue
        # and the RegScale issue already has data in the severityCheck field
        if issue["wizId"] in set_wiz_issues:
            for wiz_issue in wiz_issues:
                # concatenate the security checks because RegScale issue already has security checks populated
                if (
                    issue["wizId"] == wiz_issue["wizId"]
                    and issue["securityChecks"]
                    and issue["securityChecks"] != wiz_issue["securityChecks"]
                ):
                    issue["securityChecks"] += f'</br>{wiz_issue["securityChecks"]}'
                    issue["recommendedActions"] = wiz_issue["recommendedActions"]
                    break
                # set the RegScale issue's security checks to Wiz's security checks because it is empty
                elif (
                    issue["wizId"] == wiz_issue["wizId"]
                    and issue["securityChecks"] != wiz_issue["securityChecks"]
                ):
                    issue["securityChecks"] = wiz_issue["securityChecks"]
                    issue["recommendedActions"] = wiz_issue["recommendedActions"]
                    break
                # the securityChecks match for Wiz and RegScale, but not the recommended actions
                elif (
                    issue["wizId"] == wiz_issue["wizId"]
                    and issue["securityChecks"] == wiz_issue["securityChecks"]
                    and issue["recommendedActions"] != wiz_issue["recommendedActions"]
                ):
                    issue["recommendedActions"] = wiz_issue["recommendedActions"]
                    break
        if issue["status"] == "Closed" and not issue["dateCompleted"]:
            issue["dateCompleted"] = get_current_datetime()
        if issue["status"] == "Open":
            issue["dateCompleted"] = ""
        update_issues.append(issue)

    api.update_server(
        config=app.config,
        method="post",
        url=app.config["domain"] + "/api/issues",
        json_list=new_issues,
        message=f"[#14bfc7]Inserting {len(new_issues)} issues in RegScale.",
    )
    api.update_server(
        config=app.config,
        method="put",
        url=app.config["domain"] + "/api/issues",
        json_list=[dataclasses.asdict(iss) for iss in update_issues],
        message=f"[#15cfec]Updating {len(update_issues)} issues in RegScale.",
    )


@wiz.command()
def threats():
    """Process threats from Wiz"""
    check_license()
    logger.info("Threats - COMING SOON")


@wiz.command()
def vulnerabilities():
    """Process vulnerabilities from Wiz"""
    check_license()
    logger.info("Vulnerabilities - COMING SOON")


def fetch_report_id(app: Application, query, variables, url) -> str:
    """Fetch report ID from Wiz

    :param app: Application instance
    :param query: Query string
    :param variables: Variables
    :param url: Wiz URL
    :return: Wiz ID
    """
    try:
        resp = send_request(
            app=app,
            query=query,
            variables=variables,
            api_endpoint_url=url,
        )
        if "error" in resp.json().keys():
            error_and_exit(f'Wiz Error: {resp.json()["error"]}')
        return resp.json()["data"]["createReport"]["report"]["id"]
    except (requests.RequestException, AttributeError) as rex:
        logger.error("Unable to pull report id from requests object\n%s", rex)
    return None


def fetch_framework_report(app: Application, wiz_project_id) -> Tuple[list, list]:
    """Fetch Framework Report from Wiz

    :param app: Application instance
    :param wiz_project_id: Wiz Project ID
    :rtype: Tuple[str,str]
    """

    wiz_frameworks = fetch_frameworks(app)
    frames = [wiz["name"].replace(" ", "_") for wiz in wiz_frameworks]
    reports = [report for report in query_reports(app)]
    check = any(frame in item["name"] for item in reports for frame in frames)
    wiz_report_ids = []
    if not check:
        logger.warning(
            "No Wiz Security Framework reports found, please create one from the "
            "following list"
        )
        for i, frame in enumerate(frames):
            print(f"{i}: {frame}")
        prompt = (
            "Please enter the number of the framework that you would like to link to"
            " this project's wiz issues"
        )
        value = click.prompt(prompt, type=int)
        assert value in range(
            len(frames)
        ), "Please enter a valid number between 0 and %i" % len(frames)
        wiz_framework = wiz_frameworks[value]
        wiz_report_id = create_compliance_report(
            app=app,
            wiz_project_id=wiz_project_id,
            report_name=f"{frames[value]}_project_" f"{wiz_project_id}",
            framework_id=wiz_framework["id"],
        )
        wiz_report_ids.append(wiz_report_id)
    else:
        wiz_report_ids = [
            report["id"]
            for report in reports
            if any(frame in report["name"] for frame in frames)
        ]

    report_header = []
    report_data = []
    for wiz_report in wiz_report_ids:
        download_url = get_report_url_and_status(app, wiz_report)
        with closing(requests.get(url=download_url, stream=True, timeout=10)) as data:
            logger.info("Download URL fetched. Streaming and parsing report")
            reader = csv.reader(codecs.iterdecode(data.iter_lines(), encoding="utf-8"))
            for row in reader:
                logger.debug(row)
                if reader.line_num == 1 and not report_header:
                    report_header = row
                    continue
                report_data.append(row)
    return report_header, report_data


def fetch_frameworks(app: Application):
    """
    Fetch frameworks from Wiz
    :param url: Wiz URL
    :rtype: str List of frameworks
    """
    app = Application()
    query = """
        query SecurityFrameworkAutosuggestOptions($policyTypes: [SecurityFrameworkPolicyType!], 
        $onlyEnabledPolicies: Boolean) {
      securityFrameworks(
        first: 500
        filterBy: {policyTypes: $policyTypes, enabled: $onlyEnabledPolicies}
      ) {
        nodes {
          id
          name
        }
      }
    }
    """
    variables = {"policyTypes": "CLOUD"}
    resp = send_request(
        app=app,
        query=query,
        variables=variables,
        api_endpoint_url=app.config["wizUrl"],
    )
    if "error" in resp.json().keys():
        error_and_exit(f'Wiz Error: {resp.json()["error"]}')
    return resp.json()["data"]["securityFrameworks"]["nodes"]


def create_or_update_inventory_report(
    app: Application,
    url: str,
    rpts: dict,
    report_prefix: str,
    wiz_project_id: str,
) -> list[str]:
    """
    Create Wiz inventory report
    :param Application app: Application instance
    :param str url: URL String
    :param  dict rpts: reports from Wiz
    :param str report_prefix: Prefix of Wiz report
    :param str wiz_project_id: Wiz project ID
    :return: List of Wiz report IDs
    :rtype: list[str]
    """

    def update_config(report_ids: list[str]) -> None:
        """Update init.yaml

        :param report_ids: list of report ids
        """
        app.config["wizInventoryReportId"] = report_ids
        app.save_config(app.config)

    entities_available = 0
    if rpts:
        entities_available = sorted(
            [
                int(report["name"][-3:-1])
                for report in rpts
                if report["name"][-3:-1].isnumeric()
            ]
        ).pop()
    if "wizInventoryReportId" in app.config and isinstance(
        app.config["wizInventoryReportId"], list
    ):
        if len(app.config["wizInventoryReportId"]) != len(rpts):
            app.config["wizInventoryReportId"] = []
            for report in rpts:
                app.config["wizInventoryReportId"].append(report["id"])
            app.save_config(app.config)

    # time.sleep(CHECK_INTERVAL_FOR_DOWNLOAD_REPORT)
    report_ids = []
    if "wizEntities" not in app.config.keys() or not app.config["wizEntities"]:
        entities = (
            "DB_SERVER",
            "DOMAIN",
            "FILE_SYSTEM_SERVICE",
            "FIREWALL",
            "GATEWAY",
            "IP_RANGE",
            "KUBERNETES_CLUSTER",
            "VIRTUAL_DESKTOP",
            "VIRTUAL_MACHINE",
            "VIRTUAL_MACHINE_IMAGE",
        )
        app.config["wizEntities"] = list(entities)
        app.save_config(app.config)
    else:
        entities = app.config["wizEntities"]
    num = 0

    while num < len(entities) != entities_available:
        entities_left = len(entities[num : num + 5])

        report_name = (
            f"{report_prefix}{num}_{num+5})"
            if entities_left == 5
            else f"{report_prefix}{num}_{num+entities_left})"
        )
        report_variables = {
            "input": {
                "name": report_name,
                "type": "CLOUD_RESOURCE",
                "projectId": wiz_project_id,
                "cloudResourceParams": {
                    # "type": report_type,
                    "includeCloudNativeJSON": True,
                    "includeWizJSON": True,
                    "entityType": entities[num : num + 5]
                    if entities_left == 5
                    else entities[num : num + entities_left],
                    "cloudPlatform": [
                        "AWS",
                        "Azure",
                        "GCP",
                        "OCI",
                        "AKS",
                        "EKS",
                        "Kubernetes",
                        "GKE",
                        "OpenShift",
                        "OKE",
                        "Alibaba",
                        "vSphere",
                    ],
                },
            }
        }

        rate = None
        try:
            while rate is None:  # infinite loop
                wiz_inv_resp = send_request(
                    app=app,
                    query=CREATE_REPORT_QUERY,
                    variables=report_variables,
                    api_endpoint_url=url,
                )
                if (
                    "errors" in wiz_inv_resp.json().keys()
                    and "Rate limit exceeded"
                    in wiz_inv_resp.json()["errors"][0]["message"]
                ):
                    logger.debug(
                        "Sleeping %f",
                        wiz_inv_resp.json()["errors"][0]["extensions"]["retryAfter"],
                    )
                    time.sleep(
                        wiz_inv_resp.json()["errors"][0]["extensions"]["retryAfter"]
                    )
                    continue
                wiz_report_id = wiz_inv_resp.json()["data"]["createReport"]["report"][
                    "id"
                ]
                if wiz_report_id:
                    break
                logger.info("Successfully created %s", report_name)
        except (requests.RequestException, AttributeError, TypeError) as rex:
            error_and_exit(
                f"Unable to pull report id from requests object\n{rex}\n{wiz_inv_resp.json()}"
            )
        report_ids.append(wiz_report_id)
        num += 5

    if not report_ids:
        report_ids = (
            app.config["wizInventoryReportId"]
            if "wizInventoryReportId" in app.config
            else [report["id"] for report in rpts]
        )
    update_config(report_ids)
    return report_ids


def create_issues_report(
    app: Application,
    url: str,
    report_name: str,
    wiz_project_id: str,
    issues_severity: list,
) -> str:
    """
    Create Wiz Issues Report
    :param Application app: Application instance
    :param str url: URL String
    :param str report_name: Wiz report name
    :param str wiz_project_id: Wiz project ID
    :param list issues_severity: Severity of Wiz issues
    :return: Wiz report ID
    :rtype: str
    """
    config = app.config
    report_issue_status = ["OPEN", "IN_PROGRESS"]
    report_type = "DETAILED"  # Possible values: "STANDARD", "DETAILED"
    report_variables = {
        "input": {
            "name": report_name,
            "type": "ISSUES",
            "projectId": wiz_project_id,
            "issueParams": {
                "type": report_type,
                "issueFilters": {
                    "severity": issues_severity,
                    "status": report_issue_status,
                },
            },
        }
    }
    try:
        wiz_report_id = fetch_report_id(app, CREATE_REPORT_QUERY, report_variables, url)
        if "wizIssuesReportId" not in config:
            config["wizIssuesReportId"] = []
            config["wizIssuesReportId"]["report_id"] = None
            config["wizIssuesReportId"]["last_seen"] = None
            app.save_config(config)
        config["wizIssuesReportId"]["report_id"] = wiz_report_id
        config["wizIssuesReportId"]["last_seen"] = get_current_datetime()
        app.save_config(config)
    except AttributeError as aex:
        logger.error("Unable to pull report id from requests object\n%s", aex)
    if not wiz_report_id:
        error_and_exit(
            "Unable to find wiz report id associated with this project number, please check your Wiz Project ID."
        )
    return wiz_report_id


def map_category(asset_string: str) -> str:
    """
    category mapper
    :param str asset_string:
    :return: Category
    :rtype: str
    """
    try:
        return getattr(AssetCategory, asset_string).value
    except (KeyError, AttributeError) as ex:
        logger.warning("Unable to find %s in AssetType enum \n", ex)
        return "Software"


def query_reports(app: Application) -> list:
    """
    Query Report table from Wiz
    :param Application app:
    :return: list object from an API response from Wiz
    :rtype: list
    """
    query = """
        query ReportsTable($filterBy: ReportFilters, $first: Int, $after: String) {
          reports(first: $first, after: $after, filterBy: $filterBy) {
            nodes {
              id
              name
              type {
                id
                name
              }
              project {
                id
                name
              }
              emailTarget {
                to
              }
              parameters {
                query
                framework {
                  name
                }
                subscriptions {
                  id
                  name
                  type
                }
                entities {
                  id
                  name
                  type
                }
              }
              lastRun {
                ...LastRunDetails
              }
              nextRunAt
              runIntervalHours
            }
            pageInfo {
              hasNextPage
              endCursor
            }
            totalCount
          }
        }
        
            fragment LastRunDetails on ReportRun {
          id
          status
          failedReason
          runAt
          progress
          results {
            ... on ReportRunResultsBenchmark {
              errorCount
              passedCount
              failedCount
              scannedCount
            }
            ... on ReportRunResultsGraphQuery {
              resultCount
              entityCount
            }
            ... on ReportRunResultsNetworkExposure {
              scannedCount
              publiclyAccessibleCount
            }
            ... on ReportRunResultsConfigurationFindings {
              findingsCount
            }
            ... on ReportRunResultsVulnerabilities {
              count
            }
            ... on ReportRunResultsIssues {
              count
            }
          }
        }
    """

    # The variables sent along with the above query
    variables = {"first": 100, "filterBy": {}}

    res = send_request(
        app,
        query=query,
        variables=variables,
        api_endpoint_url=app.config["wizUrl"],
    )
    if "error" in res.json().keys():
        error_and_exit(f'Wiz Error: {res.json()["error"]}')

    result = res.json()["data"]["reports"]["nodes"]

    return result


def send_request(
    app: Application,
    query: dict,
    variables: dict,
    api_endpoint_url: str = None,
) -> requests.Response:
    """
    Send a graphQL request to Wiz.
    :param Application app:
    :param dict query: Query to use for GraphQL
    :param dict variables:
    :param str api_endpoint_url: Wiz GraphQL URL
    :raises: General Exception if the access token is missing from wizAccessToken in init.yaml
    :return: response from post call to provided api_endpoint_url
    :rtype: requests.Response
    """
    logger.debug("Sending a request to Wiz API")
    api = Api(app)
    payload = dict({"query": query, "variables": variables})
    if api_endpoint_url is None:
        api_endpoint_url = app.config["wizUrl"]
    if app.config["wizAccessToken"]:
        return api.post(
            url=api_endpoint_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + app.config["wizAccessToken"],
            },
            json=payload,
        )
    raise Exception("An access token is missing.")


def rerun_report(app: Application, report_id: str) -> str:
    """
    Rerun a Wiz Report
    :param Application app: Application instance
    :param str report_id: report id
    :return: Wiz report ID
    :rtype: str
    """
    rerun_report_query = """
        mutation RerunReport($reportId: ID!) {
            rerunReport(input: { id: $reportId }) {
                report {
                    id
                }
            }
        }
    """
    run = True
    rate = 0.5
    config = app.config
    while run:
        variables = {"reportId": report_id}
        response = send_request(app, query=rerun_report_query, variables=variables)
        if "application/json" in response.headers.get("content-type"):
            if "errors" in response.json():
                if "Rate limit exceeded" in response.json()["errors"][0]["message"]:
                    rate = response.json()["errors"][0]["extensions"]["retryAfter"]
                    time.sleep(rate)
                else:
                    # The logs contain the relevant information in case of errors
                    # API queries/variables
                    # API responses
                    error_and_exit(
                        f"Error info: {response.json()['errors']}\nVariables:{variables}\nQuery:{rerun_report_query}"
                    )
            else:
                report_id = response.json()["data"]["rerunReport"]["report"]["id"]
                logger.info("Report was re-run successfully. Report ID: %s", report_id)
                run = False
        else:
            time.sleep(rate)
            continue
    if config["wizIssuesReportId"]["report_id"] == report_id:
        config["wizIssuesReportId"]["last_seen"] = get_current_datetime()
        app.save_config(config)
    else:
        config["wizIssuesReportId"]["report_id"] = report_id
        config["wizIssuesReportId"]["last_seen"] = get_current_datetime()
        app.save_config(config)
    return report_id


def create_compliance_report(
    app: Application,
    report_name: str,
    wiz_project_id: str,
    framework_id: str,
) -> str:
    """Create Wiz compliance report

    :param app: Application instance
    :param url: Wiz URL
    :param report_name: Report name
    :param wiz_project_id: Wiz Project ID
    :param framework_id: Wiz Framework ID
    :return: Compliance Report id
    """
    report_variables = {
        "input": {
            "name": report_name,
            "type": "COMPLIANCE_ASSESSMENTS",
            "csvDelimiter": "US",
            "projectId": wiz_project_id,
            "complianceAssessmentsParams": {"securityFrameworkIds": [framework_id]},
            "emailTargetParams": None,
            "exportDestinations": None,
        }
    }

    return fetch_report_id(
        app, CREATE_REPORT_QUERY, report_variables, url=app.config["wizUrl"]
    )


def get_report_url_and_status(app: Application, report_id: str) -> str:
    """
    Generate Report URL from Wiz report
    :param Application app: Application instance
    :param str report_id: Wiz report ID
    :raises: requests.RequestException if download failed and exceeded max # of retries
    :return: URL of report
    :rtype: str
    """
    num_of_retries = 0
    while num_of_retries < MAX_RETRIES:
        variables = {"reportId": report_id}
        if num_of_retries > 0:
            logger.info(
                "Report %s is still updating, waiting %.2f seconds",
                report_id,
                CHECK_INTERVAL_FOR_DOWNLOAD_REPORT,
            )
            time.sleep(CHECK_INTERVAL_FOR_DOWNLOAD_REPORT)
        response = download_report(app, variables)
        response_json = response.json()
        if "errors" in response_json.keys():
            try:
                if (
                    "Rate limit exceeded"
                    in response_json.json()["errors"][0]["message"]
                ):
                    rate = response.json()["errors"][0]["extensions"]["retryAfter"]
                    time.sleep(rate)  # Give a bit of extra time, this is threaded.
                    logger.warning("Sleeping %i", rate)
                    continue
                logger.error(response_json["errors"])
            except AttributeError:
                continue
        status = response_json["data"]["report"]["lastRun"]["status"]
        if status == "COMPLETED":
            return response_json["data"]["report"]["lastRun"]["url"]
        num_of_retries += 1
    raise requests.RequestException(
        "Download failed, exceeding the maximum number of retries"
    )


def download_report(app: Application, variables) -> requests.Response:
    """
    Return a download URL for a provided Wiz report id
    :param app: Application instance
    :param variables: Variables for Wiz request
    :return: response from Wiz API
    :rtype: requests.Response
    """
    download_query = """
    query ReportDownloadUrl($reportId: ID!) {
        report(id: $reportId) {
            lastRun {
                url
                status
            }
        }
    }
    """
    response = send_request(app, download_query, variables=variables)
    return response


def get_asset_by_external_id(
    wiz_external_id: str, existing_ssp_assets: list[Asset]
) -> Asset:
    """Returns a single asset by the wiz external ID

    :param wiz_external_id: _description_
    :return: _description_
    """
    asset = None
    for existing_ssp_asset in existing_ssp_assets:
        if existing_ssp_asset["wizId"] == wiz_external_id:
            asset = existing_ssp_asset
    return asset


def fetch_wiz_issues(
    config: dict,
    download_url: str,
    regscale_id: int,
    regscale_module: str = "securityplans",
) -> list:
    """
    Read Stream of CSV data from a URL and process to RegScale Issues.
    :param dict config: Application configuration
    :param str download_url: WIZ download URL
    :param int regscale_id: ID # for RegScale record
    :param str regscale_module: RegScale module, defaults to securityplans
    :return: list of RegScale issues
    :rtype: list
    """
    app = Application()
    regscale_issues_from_wiz = []
    header = []
    with closing(requests.get(url=download_url, stream=True, timeout=10)) as data:
        logger.info("Download URL fetched. Streaming and parsing report")
        reader = csv.reader(codecs.iterdecode(data.iter_lines(), encoding="utf-8"))
        for row in reader:
            logger.debug(row)
            if reader.line_num == 1:
                header = row
                continue
            title = row[header.index("Title")]
            # resource = json.loads(row[header.index("Resource original JSON")])
            first_seen = convert_datetime_to_regscale_string(
                datetime.datetime.strptime(
                    row[header.index("Created At")], "%Y-%m-%dT%H:%M:%SZ"
                )
            )
            # properties = (
            #     resource["properties"] if "properties" in resource.keys() else {}
            # )
            last_seen = config["wizIssuesReportId"]["last_seen"]

            status = row[header.index("Status")]
            severity = row[header.index("Severity")]
            today_date = date.today().strftime("%m/%d/%y")
            # handle parent assignments for deep linking
            int_security_plan_id = 0
            int_component_id = 0
            int_project_id = 0
            int_supply_chain_id = 0
            if regscale_module == "projects":
                int_project_id = regscale_id
            if regscale_module == "supplychain":
                int_supply_chain_id = regscale_id
            if regscale_module == "components":
                int_component_id = regscale_id
            else:
                int_security_plan_id = regscale_id
            if severity == "LOW":
                days = check_config_for_issues(config=config, issue="wiz", key="low")
                str_severity = "III - Low - Other Weakness"
                due_date = datetime.datetime.strptime(
                    today_date, "%m/%d/%y"
                ) + datetime.timedelta(days=days)
            elif severity == "MEDIUM":
                days = check_config_for_issues(config=config, issue="wiz", key="medium")
                str_severity = "II - Moderate - Reportable Condition"
                due_date = datetime.datetime.strptime(
                    today_date, "%m/%d/%y"
                ) + datetime.timedelta(days=days)
            elif severity == "HIGH":
                days = check_config_for_issues(config=config, issue="wiz", key="high")
                str_severity = "II - Moderate - Reportable Condition"
                due_date = datetime.datetime.strptime(
                    today_date, "%m/%d/%y"
                ) + datetime.timedelta(days=days)
            elif severity == "CRITICAL":
                days = check_config_for_issues(
                    config=config, issue="wiz", key="critical"
                )
                str_severity = "I - High - Significant Deficiency"
                due_date = datetime.datetime.strptime(
                    today_date, "%m/%d/%y"
                ) + datetime.timedelta(days=days)
            else:
                logger.error("Unknown Wiz severity level: %s", severity)

            # evidence = row[header.index("Evidence")]

            description = f"""<strong>Wiz Control ID: </strong>{row[header.index('Control ID')]}<br/>\
                            <strong>Wiz Issue ID: </strong>{row[header.index('Issue ID')]}<br/>\
                            <strong>Asset Type: </strong>{row[header.index('Resource Type')]}<br/>
                            <strong>Severity: </strong>{severity}<br/> \
                            <strong>Date First Seen: </strong>{first_seen}<br/>\
                            <strong>Date Last Seen: </strong>{last_seen}<br/>\
                            <strong>Description: </strong>{row[header.index("Description")]}<br/>\
                            <strong>Remediation Recommendation: </strong>{row[header.index("Remediation Recommendation")]}<br/>\
                            """
            wiz_asset_external_id = row[header.index("Resource external ID")]
            existing_ssp_assets = Asset.find_assets_by_parent(
                app=app, parent_id=regscale_id, parent_module="securityplans"
            )
            linked_asset = get_asset_by_external_id(
                wiz_asset_external_id, existing_ssp_assets=existing_ssp_assets
            )

            issue = Issue(
                title=title,
                dateCreated=first_seen,
                status=capitalize_words(status),
                uuid=row[header.index("Issue ID")],
                securityChecks=row[
                    header.index("Description")
                ],  # TODO: Add Wiz Security Checks, verify with Dale
                severityLevel=str_severity,
                issueOwnerId=config["userId"],
                supplyChainId=int_supply_chain_id,
                securityPlanId=int_security_plan_id,
                projectId=int_project_id,
                componentId=int_component_id,
                # Defaults to SSP if no asset id is linked
                parentId=linked_asset.id if linked_asset else regscale_id,
                parentModule="assets" if linked_asset else regscale_module,
                identification="Security Control Assessment",
                dueDate=convert_datetime_to_regscale_string(due_date),
                wizId=row[header.index("Issue ID")],
                description=description,  # TODO: Add Wiz Scanner Version to description
                recommendedActions=row[header.index("Remediation Recommendation")],
            )
            regscale_issues_from_wiz.append(issue)
    logger.info(
        "Found %i Wiz Issues to update or insert into RegScale",
        len(regscale_issues_from_wiz),
    )
    return regscale_issues_from_wiz


def get_properties(app: Application, wiz_data: str, wiz_id: str) -> list[dict]:
    """
    Convert Wiz properties data into a list of dictionaries
    :param Application app: Application instance
    :param str wiz_data: Wiz information
    :param wiz_id: Wiz ID for an issue
    :return: Properties from Wiz
    :rtype: list[dict]
    """
    # loop through dict for k:v
    wiz_data = json.loads(wiz_data)
    props = []
    for k, values in recursive_items(wiz_data):
        if not isinstance(values, dict):
            if values:
                prop = {
                    "createdById": app.config["userId"],
                    "dateCreated": get_current_datetime(),
                    "lastUpdatedById": app.config["userId"],
                    "isPublic": True,
                    "wiz_id": wiz_id,
                    "key": k,
                    "value": values,
                    "parentId": 0,
                    "parentModule": "assets",
                    "dateLastUpdated": get_current_datetime(),
                }
                props.append(prop)
        else:
            for key, value in recursive_items(
                values
            ):  # I'm hitting some recursion limits here.
                if isinstance(value, dict):
                    value = json.dumps(value)
                if value:
                    prop = {
                        "createdById": app.config["userId"],
                        "dateCreated": get_current_datetime(),
                        "lastUpdatedById": app.config["userId"],
                        "isPublic": True,
                        "wiz_id": wiz_id,
                        "key": key,
                        "value": value,
                        "parentId": 0,
                        "parentModule": "assets",
                        "dateLastUpdated": get_current_datetime(),
                    }
                props.append(prop)

    return props


def check_module_id(app: Application, parent_id: int, parent_module: str) -> bool:
    """
    Verify object exists in RegScale
    :param Application app: Application object
    :param int parent_id: RegScale parent ID
    :param str parent_module: RegScale module
    :return: True or False if the object exists in RegScale
    :rtype: bool
    """
    api = Api(app)
    # increase timeout to match GraphQL timeout in the application
    api.timeout = 30
    modules = Modules()
    key = (
        list(modules.dict().keys())[list(modules.dict().values()).index(parent_module)]
    ) + "s"

    body = """
    query {
        NAMEOFTABLE(take: 50, skip: 0) {
          items {
            id
          },
          pageInfo {
            hasNextPage
          }
          ,totalCount 
        }
    }
        """.replace(
        "NAMEOFTABLE", key
    )

    items = api.graph(query=body)

    if parent_id in set(obj["id"] for obj in items[key]["items"]):
        return True
    return False
