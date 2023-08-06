#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Performs data processing for bulk processing"""

# standard python imports
import json
from os import sep
from typing import Tuple

import click
import requests

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    create_progress_object,
    save_data_to,
)
from regscale.core.app.utils.regscale_utils import get_all_from_module
from regscale.core.app.utils.threadhandler import create_threads, thread_assignment

app = Application()
config = app.config
api = Api(app)

logger = create_logger()
job_progress = create_progress_object()
process_counter = []


@click.group()
def migrations():
    """Performs data processing for legacy data to migrate data formats or perform bulk processing."""


@migrations.command(name="inheritance_converter")
def inheritance_converter():
    """
    Migrates all data from legacy one to one system to the new one to many system.
    """
    # retrieve all inherited controls
    try:
        logger.info("Retrieving all existing inherited controls")
        inheritedControls = api.get(
            url=config["domain"] + "/api/inheritance/getAllInheritedControls"
        ).json()
        logger.info(
            "%s inherited controls retrieved from RegScale.", len(inheritedControls)
        )
    except requests.exceptions.RequestException as ex:
        logger.error("Unable to retrieve inherited controls\n%s", ex)

    # output inherited controls list
    with open("./artifacts/inheritedControls.json", "w") as outfile:
        outfile.write(json.dumps(inheritedControls, indent=4))

    # loop through each inherited control
    inhNewCTRLs = []
    for inh in inheritedControls:
        bPublic = 0
        if inh["isPublic"] is True:
            bPublic = 1
        # create new control and map to new schema
        newCTRL = {
            "id": 0,
            "isPublic": bPublic,
            "parentId": int(inh["parentId"]),
            "parentModule": inh["parentModule"],
            "baseControlId": int(inh["id"]),
            "inheritedControlId": int(inh["inheritedControlId"]),
        }
        inhNewCTRLs.append(newCTRL)

    # output the new control list
    with open("./artifacts/inheritedControlMappings.json", "w") as outfile:
        outfile.write(json.dumps(inhNewCTRLs, indent=4))
    logger.info("%s controls remapped to new inheritance engine", len(inhNewCTRLs))

    # loop through and create each controls
    inheritanceNew = []
    logger.info("Beginning the process to upload and create new Inherited controls")
    url_inheritance = f'{config["domain"]}/api/inheritedControls'
    for n in inhNewCTRLs:
        try:
            print(n)
            response = api.post(url_inheritance, json=n)
            newControl = response.json()
            logger.info("New inherited control mapping: %s", newControl["id"])
            inheritanceNew.append(newControl)
        except requests.exceptions.RequestException as ex:
            print(ex)
            logger.error("Unable to save new inherited control")
            quit()

    # output the new control list
    with open("./artifacts/newInheritedControlMappings.json", "w") as outfile:
        outfile.write(json.dumps(inheritanceNew, indent=4))
    logger.info("%s controls saved to the new inheritance system", len(inheritanceNew))


@migrations.command(name="issue_linker")
def issue_linker():
    """
    Provides linkage to the lineage of the issue (deep links to parent records in the tree).
    """
    module = "issues"

    api, regscale_issues = initialize_and_fetch_data(module)

    with job_progress:
        # create task to process issues
        processing_issues = job_progress.add_task(
            f"[#f8b737]Analyzing {len(regscale_issues)} RegScale issue(s)...",
            total=len(regscale_issues),
        )

        # create threads to process the issues
        create_threads(
            process=process_data,
            args=(api, regscale_issues, module, processing_issues),
            thread_count=len(regscale_issues),
        )

        # notify user of outcome
        logger.info(
            "%s/%s %s processed from RegScale.",
            len(process_counter),
            len(regscale_issues),
            module.title(),
        )


@migrations.command(name="assessment_linker")
def assessment_linker():
    """
    Provides linkage to the lineage of the assessment (deep links to parent records in the tree).
    """
    module = "assessments"

    api, regscale_assessments = initialize_and_fetch_data(module)

    with job_progress:
        # create task to process issues
        processing_issues = job_progress.add_task(
            f"[#f8b737]Analyzing {len(regscale_assessments)} RegScale issue(s)...",
            total=len(regscale_assessments),
        )

        # create threads to process the issues
        create_threads(
            process=process_data,
            args=(api, regscale_assessments, module, processing_issues),
            thread_count=len(regscale_assessments),
        )

        # notify user of outcome
        logger.info(
            "%s/%s %s processed from RegScale.",
            len(process_counter),
            len(regscale_assessments),
            module.title(),
        )


@migrations.command(name="risk_linker")
def risk_linker():
    """
    Provides linkage to the lineage of the risk (deep links to parent records in the tree).
    """
    module = "risks"

    api, regscale_risks = initialize_and_fetch_data(module)

    with job_progress:
        # create task to process issues
        processing_issues = job_progress.add_task(
            f"[#f8b737]Analyzing {len(regscale_risks)} RegScale issue(s)...",
            total=len(regscale_risks),
        )

        # create threads to process the issues
        create_threads(
            process=process_data,
            args=(api, regscale_risks, module, processing_issues),
            thread_count=len(regscale_risks),
        )

        # notify user of outcome
        logger.info(
            "%s/%s %s processed from RegScale.",
            len(process_counter),
            len(regscale_risks),
            module.title(),
        )


def initialize_and_fetch_data(module: str) -> Tuple[Api, list[dict]]:
    """
    Function to start application, api, and fetches all records for the provided module
    from RegScale via API and saves the output to a .json file
    :param str module: python module
    :return: Tuple[Api object, list of data of provided module from RegScale API]
    :rtype: Tuple[Api, list[dict]]
    """
    # load the config from YAML
    app = Application()
    api = Api(app)

    # get the data of provided module from RegScale via API
    regscale_data = get_all_from_module(api=api, module=module)

    # verify artifacts folder exists
    check_file_path("artifacts")

    # write out risks data to file
    save_data_to(
        file_name=f"artifacts{sep}RegScale{module.title()}",
        file_type=".json",
        data=regscale_data,
    )
    logger.info(
        "Writing out RegScale risk list to the artifacts folder (see RegScale%sList.json).",
        module.title(),
    )
    logger.info(
        "%s %s retrieved for processing from RegScale.", len(regscale_data), module
    )
    return api, regscale_data


def process_data(args: Tuple, thread: int) -> None:
    """
    Function to utilize threading and process the data from RegScale
    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :raises: General error if unable to retrieve data from RegScale API
    :return: None
    """
    # set up local variables from args passed
    api, regscale_data, module, task = args

    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(regscale_data))
    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the recommendation for the thread for later use in the function
        item = regscale_data[threads[i]]

        url_processor = (
            f'{api.config["domain"]}/api/{module}/processLineage{item["id"]}'
        )
        try:
            process_result = api.get(url_processor)
            logger.info(
                "Processing %s #: %s Result: %s",
                module[:-1].title(),
                item["id"],
                process_result.text,
            )
            process_counter.append(item)
        except Exception:
            logger.error("Unable to process Issue # %s.", item["id"])
        job_progress.update(task, advance=1)
