#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Jira integration for RegScale CLI """

# Standard python imports
from json import JSONDecodeError
from os import sep
from typing import Tuple

import click
import requests
from jira import JIRA

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    create_progress_object,
    error_and_exit,
    save_data_to,
)
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.core.app.utils.threadhandler import create_threads, thread_assignment
from regscale.models import regscale_id, regscale_module

# global variables
job_progress = create_progress_object()
logger = create_logger()
update_issues = []
update_counter = []
#####################################################################################################
#
# PROCESS ISSUES TO JIRA
# JIRA CLI Python Docs: https://jira.readthedocs.io/examples.html#issues
# JIRA API Docs: https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
#
#####################################################################################################


# Create group to handle Jira integration
@click.group()
def jira():
    """Auto-assigns tickets to JIRA for remediation."""


@jira.command()
@regscale_id()
@regscale_module()
@click.option(
    "--jira_project",
    type=click.STRING,
    help="RegScale will sync the issues for the record to the Jira project.",
    prompt="Enter the name of the project in Jira",
    required=True,
)
@click.option(
    "--jira_issue_type",
    type=click.STRING,
    help="Enter the Jira issue type to use when creating new issues from RegScale.",
    prompt="Enter the Jira issue type",
    required=True,
)
def issues(
    regscale_id: int, regscale_module: str, jira_project: str, jira_issue_type: str
):
    """Process issues to Jira."""
    app = check_license()
    api = Api(app)
    config = app.config

    # see if provided RegScale Module is an accepted option
    verify_provided_module(regscale_module)

    # get secrets
    url = config["jiraUrl"]
    token = config["jiraApiToken"]
    jira_user = config["jiraUserName"]

    # set url
    url_issues = f'{config["domain"]}/api/issues/getAllByParent/{regscale_id}/{regscale_module.lower()}'

    # get the existing issues for the parent record that are already in RegScale
    logger.info("Fetching full issue list from RegScale.")
    issue_response = api.get(url_issues)
    # check for null/not found response
    if issue_response.status_code == 204:
        logger.warning("No existing issues for this RegScale record.")
        issues_data = []
    else:
        try:
            issues_data = issue_response.json()
        except JSONDecodeError as ex:
            error_and_exit(f"Unable to fetch issues from RegScale.\n{ex}")

    # make directory if it doesn't exist
    check_file_path("artifacts")

    # write issue data to a json file
    if len(issues_data) > 0:
        save_data_to(
            file_name=f"artifacts{sep}existingRecordIssues",
            file_type=".json",
            data=issues_data,
        )
        logger.info(
            "Writing out RegScale issue list for Record # %s to the artifacts folder (see existingRecordIssues.json).",
            regscale_id,
        )
    logger.info(
        "%s existing issue(s) retrieved for processing from RegScale.",
        len(issues_data),
    )
    # set the JIRA Url
    jira_client = JIRA(basic_auth=(jira_user, token), options={"server": url})
    start_pointer = 0
    page_size = 100
    jira_issues = []

    # get all issues for the Jira project
    while True:
        start = start_pointer * page_size
        fetch_jira_issues = jira_client.search_issues(
            f"project={jira_project}",
            fields="key,summary,description,status",
            startAt=start,
            maxResults=page_size,
        )
        if len(jira_issues) == fetch_jira_issues.total:
            break
        start_pointer += 1
        # append new records to jira_issues
        jira_issues.extend(fetch_jira_issues)
        logger.info(
            "%s/%s Jira issue(s) retrieved.",
            len(jira_issues),
            fetch_jira_issues.total,
        )
    logger.info("%s issue(s) retrieved from Jira.", len(jira_issues))
    # loop through each RegScale issue
    new_issue_counter = 0
    # cannot thread this process due to jira api limitations
    for issue in issues_data:
        # see if Jira ticket already exists
        if "jiraId" not in issue or issue["jiraId"] == "":
            # create the new JIRA issue
            new_issue = jira_client.create_issue(
                project=jira_project,
                summary=issue["title"],
                description=issue["description"],
                issuetype={"name": jira_issue_type},
            )
            # log progress
            new_issue_counter += 1
            logger.info(
                "%s Issue Created for RegScale Issue # %s",
                new_issue_counter,
                issue["id"],
            )
            # get the Jira ID
            jira_id = new_issue.key
            # update the RegScale issue for the Jira link
            issue["jiraId"] = jira_id
            # add the issue to the update_issues global list
            update_issues.append(issue)
    # output the final result
    logger.info("%s new issue ticket(s) opened in Jira.", new_issue_counter)
    if len(update_issues) > 0:
        with job_progress:
            # create task to update RegScale issues
            updating_issues = job_progress.add_task(
                f"[#f8b737]Updating {len(update_issues)} RegScale issue(s) with Jira ticket #(s)...",
                total=len(update_issues),
            )
            # create threads to analyze Jira issues and RegScale issues
            create_threads(
                process=update_regscale_issues,
                args=(
                    update_issues,
                    config,
                    api,
                    updating_issues,
                ),
                thread_count=len(update_issues),
            )
            # output the final result
            logger.info(
                "%s/%s issue(s) updated in RegScale.",
                len(update_issues),
                len(update_counter),
            )
    else:
        logger.info("No issues need to be updated in RegScale.")


def update_regscale_issues(args: Tuple, thread: int) -> None:
    """
    Function to compare Jira issues and RegScale issues
    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :raises: RequestException if unable to update RegScale issue
    :return: None
    """
    # set up local variables from the passed args
    (
        regscale_issues,
        config,
        api,
        task,
    ) = args

    # set the url
    reg_scale_issue_url = config["domain"] + "/api/issues/"

    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(regscale_issues))
    # update api pool limits to max_thread count from init.yaml
    api.pool_connections = config["maxThreads"]
    api.pool_maxsize = config["maxThreads"]

    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the issue for the thread for later use in the function
        issue = regscale_issues[threads[i]]
        # update the issue in RegScale
        regscale_update_url = f"{reg_scale_issue_url}{issue['id']}"
        try:
            api.put(url=regscale_update_url, json=issue)
            logger.info(
                "RegScale Issue %s was updated with the Jira link.",
                issue["id"],
            )
        except requests.exceptions.RequestException as ex:
            logger.error(ex)
        # update progress bar
        job_progress.update(task, advance=1)
