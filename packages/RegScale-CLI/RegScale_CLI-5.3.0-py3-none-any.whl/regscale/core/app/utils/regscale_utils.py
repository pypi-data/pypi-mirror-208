#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Functions used to interact with RegScale API """

# standard imports
import os
import re
import mimetypes

from requests import JSONDecodeError

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    error_and_exit,
    get_file_name,
    get_file_type,
)
from regscale.models.regscale_models.modules import Modules

logger = create_logger()


def send_email(api, domain: str, payload: dict) -> bool:
    """
    Function to use the RegScale email API and send an email, returns bool on whether API call was successful
    :param api: API object
    :param str domain: RegScale URL of instance
    :param dict payload: email payload
    :return: Boolean if RegScale api was successful
    :rtype: bool
    """
    # use the api to post the dict payload passed
    response = api.post(url=f"{domain}/api/email", json=payload)
    # see if api call was successful and return boolean
    return response.status_code == 200


def create_regscale_file(
    file_path: str, parent_id: int, parent_module: str, api
) -> list:
    """
    Function to create a file within RegScale via API
    :param str file_path: Path to the file
    :param int parent_id: RegScale parent ID
    :param str parent_module: RegScale module
    :param api: API object
    :raises: General error if unacceptable file type was provided
    :return: List of the RegScale API response
    :rtype: list
    """

    # get the file type of the provided file_path
    file_type = get_file_type(file_path)

    # get the file name from the provided file_path
    file_name = get_file_name(file_path)

    # set up file headers
    file_headers = {"Authorization": api.config["token"], "Accept": "application/json"}

    # see file_type is an acceptable format and set the file_type_header accordingly
    file_type_header = mimetypes.types_map[file_type]

    # set the files up for the RegScale API Call
    files = [("file", (file_name, open(file_path, "rb").read(), file_type_header))]

    # configure data payload
    data = {"id": parent_id, "module": parent_module}

    # make the api call
    file_response = api.post(
        url=f"{api.config['domain']}/api/files/file",
        headers=file_headers,
        data=data,
        files=files,
    )
    return file_response.json() if file_response.status_code == 200 else None


def update_regscale_config(str_param: str, val: any, app: Application = None) -> str:
    """
    Update config in init.yaml
    :param str str_param: config parameter to update
    :param any val: config parameter value to update
    :param app: Application object
    :return: Verification message
    :rtype: str
    """
    config = app.config
    # update config param
    # existing params will be overwritten, new params will be added
    config[str_param] = val
    # write the changes back to file
    app.save_config(config)
    logger.debug(f"Parameter '{str_param}' set to '{val}'.")
    return "Config updated"


def upload_file_to_regscale(
    file_name: str, parent_id: int, parent_module: str, api
) -> bool:
    """
    Function that will create and upload a file to RegScale to the provided parent_module and parent_id
    returns whether the file upload was successful or not
    :param str file_name: Path to the file to upload
    :param int parent_id: RegScale parent ID
    :param str parent_module: RegScale module
    :param api: API object
    :return: Whether the file upload was successful or not
    :rtype: bool
    """
    if regscale_file := create_regscale_file(
        file_path=file_name,
        parent_id=parent_id,
        parent_module=parent_module,
        api=api,
    ):
        # set up headers for file upload
        file_headers = {
            "Authorization": api.config["token"],
            "accept": "application/json, text/plain, */*",
        }

        # set up file_data payload with the regscale_file dictionary
        file_data = {
            "uploadedBy": "",
            "parentId": parent_id,
            "parentModule": parent_module,
            "uploadedById": api.config["userId"],
            "id": regscale_file["id"],
            "fullPath": regscale_file["fullPath"],
            "trustedDisplayName": regscale_file["trustedDisplayName"],
            "trustedStorageName": regscale_file["trustedStorageName"],
            "uploadDate": regscale_file["uploadDate"],
            "fileHash": regscale_file["fileHash"],
            "size": os.path.getsize(file_name),
        }

        # post the regscale_file data via RegScale API
        file_res = api.post(
            url=f"{api.config['domain']}/api/files",
            headers=file_headers,
            json=file_data,
        )
    else:
        error_and_exit("Unable to create RegScale file.")
    # return whether the api call was successful or not
    # right now there is a bug in the main application where it returns a 204 error code
    # which means there is no content on the file, but the file does upload successfully and has data
    return file_res.status_code in [200, 204]


def create_regscale_assessment(url: str, new_assessment: dict, api) -> int:
    """
    Function to create a new assessment in RegScale and returns the new assessment's ID
    :param str url: RegScale instance URL to create the assessment
    :param dict new_assessment: API assessment payload
    :param api: API object
    :return: New RegScale assessment ID
    :rtype: int
    """
    assessment_res = api.post(url=url, json=new_assessment)
    return assessment_res.json()["id"] if assessment_res.status_code == 200 else None


def get_issues_by_integration_field(api, field: str) -> list:
    """
    Function to get the RegScale issues for the provided integration field that has data populated
    :param api: API Object
    :param field: Integration field to filter the RegScale issues
    :raises: JSONDecodeError if API response cannot be converted to a json object
    :return: List of issues with the provided integration field populated
    :rtype: list
    """
    # set the url with the field provided
    url = f'{api.config["domain"]}/api/issues/getAllByIntegrationField/{field}'
    # get the data via API
    response = api.get(url=url)
    try:
        # try to convert the data to a json
        issues = response.json()
    except JSONDecodeError as ex:
        # unable to convert the data to a json, display error and exit
        error_and_exit(f"Unable to retrieve issues from RegScale.\n{ex}")
    # return the issues
    return issues


def verify_provided_module(module: str) -> None:
    """
    Function to check the provided module is a valid RegScale module and will display the acceptable RegScale modules
    :param str module: desired module
    :raises: General Error if the provided module is not a valid RegScale module
    :return: None
    """
    if module not in Modules().api_names():
        Modules().to_table()
        error_and_exit("Please provide an option from the Accepted Value column.")


def lookup_reg_assets_by_parent(api, parent_id: int, module: str) -> list:
    """
    Function to get assets from RegScale via API with the provided System Security Plan ID
    :param api: API object
    :param int parent_id: RegScale System Security Plan ID
    :param str module: RegScale module
    :raises: JSONDecodeError if API response cannot be converted to a json object
    :raises: General Error if API response is not successful
    :return: List of data returned from RegScale API
    :rtype: list
    """
    # verify provided module
    verify_provided_module(module)

    config = api.config
    regscale_assets_url = (
        f"{config['domain']}/api/assets/getAllByParent/{parent_id}/{module}"
    )
    results = []

    response = api.get(url=regscale_assets_url)
    if response.ok:
        try:
            results = response.json()
        except JSONDecodeError:
            logger.warning(
                f"No assets associated with the provided ID and module: {module} #{parent_id}."
            )
    else:
        error_and_exit(
            f"Unable to get assets from RegScale. Received:{response.status_code}\n{response.text}"
        )
    return results


def get_all_from_module(api, module: str) -> list[dict]:
    """
    Function to retrieve all records for the provided Module in RegScale via API
    :param api: API object
    :param str module: RegScale Module
    :raises: JSONDecodeError if API response cannot be converted to a json object
    :return: list of objects from RegScale API of the provided module
    :rtype: list[dict]
    """
    # verify provided module
    verify_provided_module(module)

    # set URL for API call
    regscale_url = f"{api.config['domain']}/api/{module}/getAll"

    logger.info("Fetching full list of %s from RegScale.", module)
    # get the full list of provided module
    try:
        regscale_response = api.get(regscale_url)
        regscale_data = regscale_response.json()
    except JSONDecodeError:
        error_and_exit(f"Unable to retrieve full list of {module} from RegScale.")
    logger.info("Retrieved %s %s from RegScale.", len(regscale_data), module)
    return regscale_data


def format_control(control: str):
    """Convert a verbose control id to a regscale friendly control id,
        e.g. AC-2 (1) becomes ac-2.1
             AC-2(1) becomes ac-2.1

    :param control: Verbose Control
    :return: RegScale friendly control
    """
    # Define a regular expression pattern to match the parts of the string
    # pattern = r'^([A-Z]{2})-(\d+)\s\((\d+)\)$'
    pattern = r"^([A-Z]{2})-(\d+)\s?\((\d+)\)$"

    # Use re.sub() to replace the matched parts of the string with the desired format
    new_string = re.sub(pattern, r"\1-\2.\3", control)

    return new_string.lower()  # Output: ac-2.1


def get_user(api, user_id: str) -> list:
    """
    Function to get the provided user_id from RegScale via API
    :param api: API Object
    :param str user_id: the RegScale user's GUID
    :raises: JSONDecodeError if API response cannot be converted to a json object
    :return: list containing the user's information
    :rtype: str
    """
    user_data = []
    url = f'{api.config["domain"]}/api/accounts/find/{user_id}'

    response = api.get(url)
    try:
        user_data = response.json()
    except JSONDecodeError:
        logger.error(
            "Unable to retrieve user from RegScale for the provided user id: %s",
            user_id,
        )

    return user_data
