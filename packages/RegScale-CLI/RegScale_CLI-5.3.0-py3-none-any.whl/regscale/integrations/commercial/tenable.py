#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Tenable integration for RegScale CLI """

# standard python imports
import collections
import dataclasses
import os
import re
import warnings
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import click
import matplotlib.pyplot as plt
import pandas as pd
import requests
from requests.exceptions import RequestException
from rich.console import Console
from rich.pretty import pprint
from rich.progress import track
from tenable.sc import TenableSC

from regscale import __version__
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    epoch_to_datetime,
    error_and_exit,
    get_current_datetime,
    save_data_to,
)
from regscale.validation.address import validate_mac_address
from regscale.core.app.utils.regscale_utils import lookup_reg_assets_by_parent
from regscale.models.app_models.click import file_types, save_output_to
from regscale.models.integration_models.tenable import TenableAsset
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue

console = Console()

logger = create_logger()
app = Application()
api = Api(app)


#####################################################################################################
#
# Tenable.sc Documentation: https://docs.tenable.com/tenablesc/api/index.htm
# pyTenable GitHub repo: https://github.com/tenable/pyTenable
# Python tenable.sc documentation: https://pytenable.readthedocs.io/en/stable/api/sc/index.html
#
#####################################################################################################


# Create group to handle OSCAL processing
@click.group()
def tenable():
    """Performs actions on the Tenable.sc API."""


@tenable.command(name="export_scans")
@save_output_to()
@file_types([".json", ".csv", ".xlsx"])
def export_scans(save_output_to: Path, file_type: str):
    """Export scans from Tenable Host to a .json, .csv or .xlsx file."""
    # get the scan results
    results = get_usable_scan_list()

    # check if file path exists
    check_file_path(save_output_to)

    # set the file name
    file_name = f"tenable_scans_{get_current_datetime('%m%d%Y')}"

    # save the data as the selected file by the user
    save_data_to(
        file_name=f"{save_output_to}{os.sep}{file_name}",
        file_type=file_type,
        data=results,
    )


def get_usable_scan_list() -> list:
    """
    Usable Scans from Tenable Host
    :return: List of scans from Tenable
    :rtype: list
    """
    results = []
    try:
        tsc = gen_tsc()
        results = tsc.scans.list()["usable"]
    except Exception as ex:
        logger.error(ex)
    return results


def get_detailed_scans(scan_list: list = None) -> list:
    """
    Generate list of detailed scans (Warning: this action could take 20 minutes or more to complete)
    :param list scan_list: List of scans from Tenable, defaults to usable_scan_list
    :return: Detailed list of Tenable scans
    :rtype: list
    """
    tsc = gen_tsc()
    detailed_scans = []
    for scan in track(scan_list, description="Fetching detailed scans..."):
        try:
            det = tsc.scans.details(id=scan["id"])
            detailed_scans.append(det)
        except RequestException as ex:  # This is the correct syntax
            raise SystemExit(ex) from ex

    return detailed_scans


@tenable.command(name="save_queries")
@save_output_to()
@file_types([".json", ".csv", ".xlsx"])
def save_queries(save_output_to: Path, file_type: str):
    """Get a list of query definitions and save them as a .json, .csv or .xlsx file."""
    # get the queries from Tenable
    query_list = get_queries()

    # check if file path exists
    check_file_path(save_output_to)

    # set the file name
    file_name = f"tenable_queries_{get_current_datetime('%m%d%Y')}"

    # save the data as a .json file
    save_data_to(
        file_name=f"{save_output_to}{os.sep}{file_name}",
        file_type=file_type,
        data=query_list,
    )


def get_queries() -> None:
    """
    List of query definitions
    :return: None
    """
    tsc = gen_tsc()
    return tsc.queries.list()


@tenable.command(name="query_vuln")
@click.option(
    "--query_id",
    type=click.INT,
    help="Tenable query ID to retrieve via API",
    prompt="Enter Tenable query ID",
    required=True,
)
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
@click.option(
    "--create_issue_from_recommendation",
    type=click.BOOL,
    help="Create Issue in RegScale from Vulnerability in RegScale.",
    default=False,
    required=False,
)
# Add Prompt for RegScale SSP name
def query_vuln(
    query_id: int, regscale_ssp_id: int, create_issue_from_recommendation: bool
):
    """Query Tenable vulnerabilities and sync assets to RegScale."""
    q_vuln(
        query_id=query_id,
        ssp_id=regscale_ssp_id,
        create_issue_from_recommendation=create_issue_from_recommendation,
    )


@tenable.command(name="trend_vuln")
@click.option(
    "-p",
    "--plugins",
    multiple=True,
    help="Enter one or more pluginID's separated by a space to see a trend-line. (by report date)",
    prompt="Enter one or more pluginID's",
    required=True,
)
@click.option(
    "-d",
    "--dnsname",
    multiple=False,
    type=click.STRING,
    help="Enter DNS name of asset to trend.",
    prompt="Enter DNS name of asset",
    required=True,
)
def trend_vuln(plugins: list, dnsname: str):
    """
    Trend vulnerabilities from vulnerability scans.
    """
    plugins = list(plugins)
    logger.info(plugins)
    trend_vulnerabilities(filter=plugins, dns=dnsname)


def q_vuln(query_id: int, ssp_id: int, create_issue_from_recommendation: bool) -> list:
    """
    Query Tenable vulnerabilities
    :param int query_id: Tenable query ID
    :param int ssp_id: RegScale System Security Plan ID
    :param bool create_issue_from_recommendation: Whether to create an issue in RegScale
    :raises: General error if asset doesn't have an ID
    :raises: requests.RequestException if unable to update asset via RegScale API
    :return: List of queries from Tenable
    :rtype: list
    """
    # At SSP level, provide a list of vulnerabilities and the counts of each
    # Normalize the data based on mac address
    reg_assets = lookup_reg_assets_by_parent(
        api=api, parent_id=ssp_id, module="securityplans"
    )

    tenable_data = fetch_vulns(query_id=query_id, regscale_ssp_id=ssp_id)
    tenable_vulns = tenable_data[0]
    tenable_df = tenable_data[1]

    assets_to_be_inserted = list(
        {
            dat
            for dat in tenable_vulns
            if dat.macAddress
            not in {asset.macAddress for asset in inner_join(reg_assets, tenable_vulns)}
        }
    )
    counts = collections.Counter(s.pluginName for s in tenable_vulns)
    update_assets = []
    insert_assets = []
    for vuln in set(tenable_vulns):  # you can list as many input dicts as you want here
        vuln.counts = dict(counts)[vuln.pluginName]
        lookup_assets = lookup_asset(reg_assets, vuln.macAddress, vuln.dnsName)
        # Update parent id to SSP on insert
        if len(lookup_assets) > 0:
            for asset in set(lookup_assets):
                # Do update
                # asset = reg_asset[0]
                asset.parentId = ssp_id
                asset.parentModule = "securityplans"
                asset.macAddress = vuln.macAddress.upper()
                asset.osVersion = vuln.operatingSystem
                asset.purchaseDate = "01-01-1970"
                asset.endOfLifeDate = "01-01-1970"
                if asset.ipAddress is None:
                    asset.ipAddress = vuln.ipAddress
                asset.operatingSystem = determine_os(asset.operatingSystem)
                try:
                    assert asset.id
                    # avoid duplication
                    if asset.macAddress.upper() not in set(
                        v["macAddress"].upper() for v in update_assets
                    ):
                        update_assets.append(asdict(asset))
                except AssertionError as aex:
                    logger.error(
                        "Asset does not have an id, unable to update!\n%s", aex
                    )

    if len(assets_to_be_inserted) > 0:
        for t_asset in assets_to_be_inserted:
            # Do Insert
            r_asset = Asset(
                name=t_asset.dnsName,
                otherTrackingNumber=t_asset.pluginID,
                parentId=ssp_id,
                parentModule="securityplans",
                ipAddress=t_asset.ip,
                macAddress=t_asset.macAddress,
                assetOwnerId=app.config["userId"],
                status=get_status(t_asset),
                assetType="Other",
                assetCategory="Hardware",
                operatingSystem=determine_os(t_asset.operatingSystem),
            )
            # avoid duplication
            if r_asset.macAddress.upper() not in set(
                v["macAddress"].upper() for v in insert_assets
            ):
                insert_assets.append(asdict(r_asset))
    try:
        headers = {
            "Authorization": app.config["token"],
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        api.update_server(
            method="post",
            headers=headers,
            url=app.config["domain"] + "/api/assets",
            json_list=insert_assets,
            message=f"Inserting {len(insert_assets)} assets from this Tenable query to RegScale.",
        )

        logger.info("RegScale Assets successfully inserted: %i.", len(insert_assets))
    except requests.exceptions.RequestException as rex:
        logger.error("Unable to Insert Tenable Assets to RegScale.\n%s", rex)
    try:
        api.update_server(
            method="put",
            url=app.config["domain"] + "/api/assets",
            json_list=update_assets,
            message=f"Updating {len(update_assets)} assets from this Tenable query to RegScale.",
        )
        logger.info("RegScale Assets successfully updated: %i.", len(update_assets))
    except requests.RequestException as rex:
        logger.error("Unable to Update Tenable Assets to RegScale.\n%s", rex)
    if create_issue_from_recommendation:
        today = get_current_datetime(dt_format="%Y-%m-%d")
        create_regscale_issue_from_vuln(
            regscale_ssp_id=ssp_id, df=tenable_df[tenable_df["report_date"] == today]
        )
    return update_assets


def determine_os(os_string: str) -> str:
    """
    Determine RegScale friendly OS name
    :param str os_string: String of the asset's OS
    :return: RegScale acceptable OS
    :rtype: str
    """
    linux_words = ["linux", "ubuntu", "hat", "centos", "rocky", "alma", "alpine"]
    if re.compile("|".join(linux_words), re.IGNORECASE).search(os_string):
        return "Linux"
    elif (os_string.lower()).startswith("windows"):
        return "Windows Server" if "server" in os_string else "Windows Desktop"
    else:
        return "Other"


def get_status(asset: TenableAsset) -> str:
    """
    Convert Tenable asset status to RegScale asset status
    :param TenableAsset asset: Asset object from Tenable
    :return: RegScale status
    :rtype: str
    """
    if asset.family.type == "active":
        return "Active (On Network)"
    return "Off-Network"  # Probably not correct


def format_vulns():
    """_summary_"""


def lookup_asset(asset_list: list, mac_address: str, dns_name: str = None) -> list:
    """
    Lookup asset in Tenable and return the data from Tenable
    :param list asset_list: List of assets to lookup in Tenable
    :param str mac_address: Mac address of asset
    :param str dns_name: DNS Name of the asset, defaults to None
    :return: List of assets that fit the provided filters
    :rtype: list
    """
    results = []
    if validate_mac_address(mac_address):
        if dns_name:
            results = [
                Asset.from_dict(asset)
                for asset in asset_list
                if asset["macAddress"] == mac_address and asset["name"] == dns_name
            ]
        else:
            results = [
                Asset.from_dict(asset)
                for asset in asset_list
                if asset["macAddress"] == mac_address
            ]
    # Return unique list
    return list(set(results))


def trend_vulnerabilities(
    filter: list,
    dns: str,
    filter_type="pluginID",
    filename="vulnerabilities.pkl",
) -> None:
    """
    Trend vulnerabilities data to the console
    :param list filter: Data to use for trend graph
    :param str dns: DNS to filter data
    :param str filter_type: Type of filter to apply to data
    :param str filename: Name of the file to save as
    :return: None
    """
    if not filter:
        return
    df = pd.read_pickle(filename)
    df = df[df[filter_type].isin(filter)]
    df = df[df["dnsName"] == dns]
    unique_cols = ["pluginID", "dnsName", "severity", "report_date"]
    df = df[unique_cols]
    df = df.drop_duplicates(subset=unique_cols)
    if len(df) == 0:
        error_and_exit("No Rows in Dataframe.")

    df.loc[df["severity"] == "Info", "severity_code"] = 0
    df.loc[df["severity"] == "Low", "severity_code"] = 1
    df.loc[df["severity"] == "Medium", "severity_code"] = 2
    df.loc[df["severity"] == "High", "severity_code"] = 3
    df.loc[df["severity"] == "Critical", "severity_code"] = 4
    # Deal with linux wayland sessions
    if "XDG_SESSION_TYPE" in os.environ and os.getenv("XDG_SESSION_TYPE") == "wayland":
        os.environ["QT_QPA_PLATFORM"] = "wayland"
    # plotting graph
    for d in filter:
        plt.plot(df["report_date"], df["severity_code"], label=d)
    logger.info("Plotting %s rows of data.\n", len(df))
    logger.info(df.head())
    plt.legend()
    plt.show(block=True)


def create_regscale_issue_from_vuln(regscale_ssp_id: int, df: pd.DataFrame) -> None:
    """
    Sync Tenable Vulnerabilities to RegScale issues
    :param int regscale_ssp_id: RegScale System Security Plan ID
    :param pd.Dataframe df: Pandas dataframe of Tenable data
    :return: None
    """
    default_status = app.config["issues"]["tenable"]["status"]
    regscale_new_issues = []
    regscale_existing_issues = []
    existing_issues_req = api.get(
        app.config["domain"]
        + f"/api/issues/getAllByParent/{regscale_ssp_id}/securityplans"
    )
    if existing_issues_req.status_code == 200:
        regscale_existing_issues = existing_issues_req.json()
    columns = list(df.columns)
    for index, row in df.iterrows():
        if df["severity"][index] != "Info":
            if df["severity"][index] == "Critical":
                default_due_delta = app.config["issues"]["tenable"]["critical"]
            elif df["severity"][index] == "High":
                default_due_delta = app.config["issues"]["tenable"]["high"]
            else:
                default_due_delta = app.config["issues"]["tenable"]["moderate"]
            logger.debug("Processing row: %i.", index + 1)
            fmt = "%Y-%m-%d %H:%M:%S"
            plugin_id = row[columns.index("pluginID")]
            port = row[columns.index("port")]
            protocol = row[columns.index("protocol")]
            due_date = datetime.strptime(
                row[columns.index("last_scan")], fmt
            ) + timedelta(days=default_due_delta)
            if row[columns.index("synopsis")]:
                title = row[columns.index("synopsis")]
            issue = Issue(
                title=title if title else row[columns.index("pluginName")],
                description=row[columns.index("description")]
                if row[columns.index("description")]
                else row[columns.index("pluginName")]
                + f"<br>Port: {port}<br>Protocol: {protocol}",
                issueOwnerId=app.config["userId"],
                status=default_status,
                severityLevel=Issue.assign_severity(row[columns.index("severity")]),
                dueDate=due_date.strftime(fmt),
                identification="Vulnerability Assessment",
                parentId=row[columns.index("regscale_ssp_id")],
                parentModule="securityplans",
                pluginId=plugin_id,
                vendorActions=row[columns.index("solution")],
                assetIdentifier=f'DNS: {row[columns.index("dnsName")]} - IP: {row[columns.index("ip")]}',
            )
            if issue.title in set([iss["title"] for iss in regscale_new_issues]):
                # Update
                update_issue = [
                    iss for iss in regscale_new_issues if iss["title"] == issue.title
                ][0]
                if update_issue["assetIdentifier"] != issue.assetIdentifier:
                    assets = set(update_issue["assetIdentifier"].split("<br>"))
                    if issue.assetIdentifier not in assets:
                        update_issue["assetIdentifier"] = (
                            update_issue["assetIdentifier"]
                            + "<br>"
                            + issue.assetIdentifier
                        )
            else:
                if issue.title not in set(
                    [iss["title"] for iss in regscale_existing_issues]
                ):
                    # Add
                    regscale_new_issues.append(dataclasses.asdict(issue))
        else:
            logger.debug("Row %i not processed: %s.", index, row["description"])
    logger.info(
        f"Posting {len(regscale_new_issues)} new issues to RegScale condensed from {len(df)} Tenable vulnerabilities."
    )
    if len(regscale_new_issues) > 0:
        api.update_server(
            url=app.config["domain"] + "/api/issues",
            message=f"Posting {len(regscale_new_issues)} issues...",
            json_list=regscale_new_issues,
        )


def log_vulnerabilities(
    data: list, query_id: int, regscale_ssp_id: int
) -> pd.DataFrame:
    """
    Logs Vulnerabilities to a panda's dataframe
    :param list data: Raw data of Tenable vulnerabilities
    :param int query_id: Query ID for Tenable query
    :param int regscale_ssp_id: RegScale System Security Plan ID
    :raises: pd.errors.DataError if unable to convert data to panda's dataframe
    :return: Cleaned up data of Tenable vulnerabilities
    :rtype: pd.DataFrame
    """
    warnings.filterwarnings("ignore", category=FutureWarning)
    try:
        df = pd.DataFrame(data)
        df["query_id"] = query_id
        df["regscale_ssp_id"] = regscale_ssp_id
        df["first_scan"] = df["firstSeen"].apply(epoch_to_datetime)
        df["last_scan"] = df["lastSeen"].apply(epoch_to_datetime)
        df["severity"] = [d.get("name") for d in df["severity"]]
        df["family"] = [d.get("name") for d in df["family"]]
        df["repository"] = [d.get("name") for d in df["repository"]]
        df["report_date"] = get_current_datetime(dt_format="%Y-%m-%d")
        filename = "vulnerabilities.pkl"

        df.drop_duplicates()
        if not Path(filename).exists():
            logger.info("Saving vulnerability data to %s.", filename)
        else:
            logger.info(
                "Updating vulnerabilities.pkl with the latest data from Tenable."
            )
            old_df = pd.read_pickle(filename)
            old_df = old_df[
                old_df["report_date"] != get_current_datetime(dt_format="%Y-%m-%d")
            ]
            try:
                df = pd.concat([old_df, df]).drop_duplicates()
            except ValueError as vex:
                logger.error("Pandas ValueError:%s.", vex)
        df.to_pickle(filename)
        severity_arr = df.groupby(["severity", "repository"]).size().to_frame()
        console.rule("[bold red]Vulnerability Overview")
        console.print(severity_arr)
        return df

    except pd.errors.DataError as dex:
        logger.error(dex)


def fetch_vulns(query_id: int, regscale_ssp_id: int) -> Tuple[list, pd.DataFrame]:
    """
    Fetch vulnerabilities from Tenable by query ID
    :param int query_id: Tenable query ID
    :param int regscale_ssp_id: RegScale System Security Plan ID
    :return: Tuple[list of vulnerabilities from Tenable, Tenable vulnerabilities as a panda's dataframe]
    :rtype: Tuple[list, pd.DataFrame]
    """
    tsc = gen_tsc()
    data = []
    if query_id:
        description = f"Fetching Vulnerabilities for Tenable query id: {query_id}."
        vulns = tsc.analysis.vulns(query_id=query_id)
        data.extend(
            TenableAsset.from_dict(vuln)
            for vuln in track(vulns, description=description, show_speed=False)
        )
        logger.info("Found %i vulnerabilities.", len(data))
    df = log_vulnerabilities(data, query_id=query_id, regscale_ssp_id=regscale_ssp_id)
    return data, df


@tenable.command(name="list_tags")
def list_tags():
    """
    Query a list of tags on the server and print to console.
    :return: None
    """
    tag_list = get_tags()
    pprint(tag_list)


def get_tags() -> list:
    """
    List of Tenable query definitions
    :return: List of unique tags for Tenable queries
    :rtype: list
    """
    tsc = gen_tsc()
    return tsc.queries.tags()


def gen_tsc() -> TenableSC:
    """
    Generate Tenable Object
    :return: Tenable client
    :rtype: TenableSC
    """
    config = Application().config
    return TenableSC(
        url=config["tenableUrl"],
        access_key=config["tenableAccessKey"],
        secret_key=config["tenableSecretKey"],
        vendor="RegScale, Inc.",
        product="RegScale CLI",
        build=__version__,
    )


def inner_join(reg_list: list, tenable_list: list) -> list:
    """
    Function to inner join two lists on the macAddress field and returns the assets existing in RegScale and Tenable
    :param list reg_list: List of RegScale assets
    :param list tenable_list: List of Tenable assets
    :raises: KeyError if macAddress isn't a key within the tenable_list
    :return: Returns list of assets that exists in RegScale and Tenable using the mac address
    :rtype: list
    """
    set1 = set(lst["macAddress"].lower() for lst in reg_list)
    data = []
    try:
        data = [
            list_ten for list_ten in tenable_list if list_ten.macAddress.lower() in set1
        ]
    except KeyError as ex:
        logger.error(ex)
    return data
