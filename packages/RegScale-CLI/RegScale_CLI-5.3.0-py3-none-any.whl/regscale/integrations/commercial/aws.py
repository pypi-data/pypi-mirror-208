#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" RegScale AWS Audit Manager Integration """

import dataclasses
import itertools
import operator
import re
from datetime import datetime, timedelta

import boto3
import click
from botocore.exceptions import ClientError

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    convert_datetime_to_regscale_string,
    format_data_to_html,
    reformat_str_date,
)
from regscale.core.app.utils.regscale_utils import format_control
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.checklist import Checklist
from regscale.models.regscale_models.control_implementation import ControlImplementation
from regscale.models.regscale_models.issue import Issue

client = boto3.client("securityhub", region_name="us-east-1")
logger = create_logger()


# Create group to handle AWS integration
@click.group()
def aws():
    """AWS Integrations"""


@aws.command(name="sync_findings")
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    required=True,
    prompt="Enter RegScale System Security Plan ID",
    help="The ID number from RegScale of the System Security Plan",
)
@click.option(
    "--create_issue",
    type=click.BOOL,
    required=False,
    help="Create Issue in RegScale from vulnerabilities in AWS Security Hub.",
    default=False,
)
def sync_findings(regscale_ssp_id: int, create_issue: bool = False) -> dict:
    """Sync AWS Security Hub Findings.
    :param regscale_ssp_id: RegScale System Security Plan ID
    :param create_issue: Create Issue in RegScale from vulnerabilities in AWS Security Hub.
    :return: dict Return AWS Assessment Report
    """

    findings = fetch_aws_findings(aws_client=client)
    fetch_aws_findings_and_sync_regscale(regscale_ssp_id, create_issue, findings)


def update_implementations(app, regscale_ssp_id):
    """Update Control Implementations.

    :param app: Application instance
    :param regscale_ssp_id: RegScale System Security Plan ID
    """
    api = Api(app)
    # Loop through checklists and updating implementations if they exist
    existing_checklists = Checklist.get_checklists(
        parent_id=regscale_ssp_id, parent_module="securityplans"
    )

    # Get the list of controls from the checklists
    failed_checklist_controls = []
    for checklist in existing_checklists:
        pattern = r"NIST\.800-53\.r5 ([A-Z]{2}-\d+\(\w\)|[A-Z]{2}-\d+|\w+-\d+\(\w\))"
        matches = re.findall(pattern, checklist["results"])
        if matches:
            # if checklist fails, add to list of controls
            if checklist["status"] == "Fail":
                failed_checklist_controls.extend(matches)

    # Update the control implementations
    existing_ssp_implementations = ControlImplementation.fetch_existing_implementations(
        app=app, regscale_parent_id=regscale_ssp_id, regscale_module="securityplans"
    )
    for control in failed_checklist_controls:
        control_id = format_control(control)
        control_implementation_data = [
            control
            for control in existing_ssp_implementations
            if control["controlName"] == control_id
        ]
        # update control implementation
        if control_implementation_data:
            control_implementation = control_implementation_data[0]
            control_implementation["status"] = "Not Implemented"
            res = api.put(
                url=app.config["domain"]
                + f"/api/controlimplementation/{control_implementation['id']}",
                json=control_implementation,
            )
            if not res.raise_for_status():
                logger.info(
                    "Successfully updated control %s",
                    control_implementation["controlName"],
                )
        else:
            logger.info("No control implementation found for %s", control_id)


def check_finding_severity(comment) -> str:
    """Check the severity of the finding.

    :param comment: Comment from AWS Security Hub finding
    :return: Severity of the finding
    """
    result = None
    match = re.search(r"(?<=Finding Severity: ).*", comment)
    if match:
        severity = match.group()
        result = severity  # Output: "High"
    return result


def extract_severities(checklists: list[Checklist]) -> str:
    """Extract severities from a list of checklists, return the highest severity found.

    :param checklists: list of Checklist
    :return: Highest severity found
    """
    severities = {check_finding_severity(chk["comments"]) for chk in checklists}
    if any(item in ["HIGH", "CRITICAL"] for item in severities):
        return "High"
    if "MEDIUM" in severities:
        return "Moderate"
    return "Low"


def create_or_update_regscale_issue(
    app: Application,
    checklists: list[Checklist],
    regscale_ssp_id: int,
    existing_issues: list[dict],
) -> None:
    """Create Issues in RegScale for failed AWS Security Checks.

    :param app: Application
    :param checklists: List of AWS Security Checks
    :param regscale_ssp_id: RegScale System Security Plan ID
    :param existing_issues: List of existing issues in RegScale
    """
    api = Api(app)
    # create issue if failed
    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"

    if isinstance(checklists[0], Checklist):
        checklists = [dataclasses.asdict(chk) for chk in checklists]
    earliest_date_performed = min(chk["datePerformed"] for chk in checklists)
    # create or update issue
    asset_link = f"""<a href="{app.config['domain']}/assets/form/{checklists[0]['assetId']}" \
        " title="Link">Asset</a>:<br></br><br>"""
    rules = {chk["ruleId"] for chk in checklists}
    failed_checks = [chk for chk in checklists if chk["status"] == "Fail"]
    days = app.config["issues"]["aws"][extract_severities(checklists).lower()]
    try:
        due_date = datetime.strptime(earliest_date_performed, fmt) + timedelta(
            days=days
        )
    except ValueError:
        due_date = datetime.strptime(
            earliest_date_performed, "%Y-%m-%dT%H:%M:%SZ"
        ) + timedelta(days)
    issue = Issue(
        title=f"Failed Security Check(s) on AWS asset: {checklists[0]['assetId']}",
        description=f"AWS Security Checks performed on {asset_link}"
        f" {'</br><br>'.join(rules)} </br>",
        issueOwnerId=app.config["userId"],
        status="Open" if "Fail" in {chk["status"] for chk in checklists} else "Closed",
        severityLevel="IV - Not Assigned",
        dueDate=due_date.strftime(fmt),
        dateCompleted=None
        if "Fail" in {chk["status"] for chk in checklists}
        else convert_datetime_to_regscale_string(datetime.now()),
        parentId=regscale_ssp_id,
        parentModule="securityplans",
        recommendedActions="See Recommendations in these failed checklists"
        if len(failed_checks) > 0
        else "No critical or high recommendations available",
        identification="Vulnerability Assessment",
    )
    if (
        issue["title"] not in {iss["title"] for iss in existing_issues}
        and issue["status"] == "Open"
    ):
        # post
        res = api.post(
            url=app.config["domain"] + "/api/issues", json=dataclasses.asdict(issue)
        )
        if not res.raise_for_status():
            logger.info("Successfully created issue %s", issue["title"])
    else:
        # update
        matches = {
            iss["id"] for iss in existing_issues if iss["title"] == issue["title"]
        }
        if matches:
            issue.id = matches.pop()
            res = api.put(
                url=app.config["domain"] + f"/api/issues/{str(issue.id)}",
                json=dataclasses.asdict(issue),
            )
            if not res.raise_for_status():
                logger.info("Successfully updated issue %s", issue.title)


def create_or_update_regscale_checklists(*args) -> Checklist:
    """Create or Update RegScale Checklists.
    :param args: Tuple of parameters

    :return: A new security checklist
    """
    app, finding, resource, regscale_ssp_id, existing_assets, existing_checklists = args

    existing_asset_id = 0
    new_asset = Asset(
        name=resource["Id"],
        status="Active (On Network)",
        assetOwnerId=app.config["userId"],
        assetCategory="Software",
        description=format_data_to_html(resource),
        assetType="Other",
        parentId=regscale_ssp_id,
        parentModule="securityplans",
        otherTrackingNumber=resource["Id"],
    )
    if new_asset.name not in {asset["name"] for asset in existing_assets}:
        existing_asset_id = Asset.insert_asset(app=app, obj=new_asset).json()["id"]
    else:
        existing_asset_id = [
            asset.id for asset in existing_assets if asset.name == new_asset.name
        ][0]
    # Create or update Checklist
    status = "Pass"
    results = None
    if "Compliance" in finding.keys():
        status = "Fail" if finding["Compliance"]["Status"] == "FAILED" else "Pass"
        results = ", ".join(finding["Compliance"]["RelatedRequirements"])
    if "FindingProviderFields" in finding.keys():
        status = (
            "Fail"
            if finding["FindingProviderFields"]["Severity"]["Label"]
            in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            else "Pass"
        )
    if "PatchSummary" in finding.keys() and not results:
        results = (
            f"{finding['PatchSummary']['MissingCount']} Missing Patch(s) of "
            "{finding['PatchSummary']['InstalledCount']}"
        )

    new_checklist = Checklist(
        assetId=existing_asset_id,
        status=status,
        tool="Other",
        datePerformed=finding["UpdatedAt"]
        if reformat_str_date(finding["UpdatedAt"])
        else reformat_str_date(datetime.now()),
        vulnerabilityId=finding["Id"],
        ruleId=finding["Title"],
        baseline=finding["GeneratorId"],
        check=finding["Description"],
        results=results,
        comments=finding["Remediation"]["Recommendation"]["Text"]
        + "<br></br>"
        + finding["Remediation"]["Recommendation"]["Url"]
        + "<br></br>"
        + f"""Finding Severity: {finding["FindingProviderFields"]["Severity"]["Label"]}""",
    )
    new_checklist.id = Checklist.insert_or_update_checklist(
        app=app,
        new_checklist=new_checklist,
        existing_checklists=existing_checklists,
    )
    return new_checklist


def fetch_aws_findings(aws_client) -> list:
    """Fetch AWS Findings

    :param aws_client: AWS Security Hub Client
    :return: AWS Findings
    """
    findings = []
    try:
        findings = aws_client.get_findings()["Findings"]
    except ClientError as cex:
        logger.error("Unexpected error: %s", cex)
    return findings


def fetch_aws_findings_and_sync_regscale(
    regscale_ssp_id: int, create_issue: bool = False, findings: list = None
) -> None:
    """Sync AWS Security Hub Findings with RegScale
    :param regscale_ssp_id: RegScale System Security Plan ID
    :param create_issue: Create Issue in RegScale from vulnerabilities in AWS Security Hub.
    :param findings: List of AWS Security Hub Findings
    :return: dict Return AWS Assessment Report
    """
    app = Application()
    existing_assets = Asset.find_assets_by_parent(
        app=app, parent_id=regscale_ssp_id, parent_module="securityplans"
    )
    existing_checklists = Checklist.get_checklists(
        parent_id=regscale_ssp_id, parent_module="securityplans"
    )
    for finding in findings:
        # Create or update Assets
        for resource in finding["Resources"]:
            create_or_update_regscale_checklists(
                app,
                finding,
                resource,
                regscale_ssp_id,
                existing_assets,
                existing_checklists,
            )
    update_implementations(app, regscale_ssp_id)
    existing_issues = Issue.fetch_issues_by_parent(
        app=app, regscale_id=regscale_ssp_id, regscale_module="securityplans"
    )
    get_attr = operator.attrgetter("assetId")

    if create_issue:
        # Refresh existing checklists
        existing_checklists = Checklist.get_checklists(
            parent_id=regscale_ssp_id, parent_module="securityplans"
        )
        checklists_grouped = [
            list(g)
            for _, g in itertools.groupby(
                sorted(
                    [Checklist.from_dict(chk) for chk in existing_checklists],
                    key=get_attr,
                ),
                get_attr,
            )
        ]
        for checklist in checklists_grouped:
            create_or_update_regscale_issue(
                app=app,
                checklists=checklist,
                regscale_ssp_id=regscale_ssp_id,
                existing_issues=existing_issues,
            )
