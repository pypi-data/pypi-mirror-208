#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module to allow user to login to RegScale """


# standard python imports
import contextlib
import logging
import sys
from datetime import datetime
from json import JSONDecodeError
from ssl import SSLCertVerificationError
from typing import Tuple

import requests

from regscale.core.app.api import Api, normalize_url
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger

logger = create_logger()


def login(
    str_user: str, str_password: str, host: str = None, app: Application = None
) -> str:
    """
    Wrapper for Login to RegScale
    :param str str_user: username to log in with
    :param str str_password: password of provided user
    :param str host: host to log into, defaults to None
    :param app: Application object
    :raises: ValueError if no domain value found in init.yaml
    :raises: TypeError if token or user id doesn't match expected data type
    :raises: SSLCertVerificationError if unable to validate SSL certificate
    :return: JWT after authentication
    :rtype: str
    """
    config = app.config
    token = None
    if config["domain"] is None:
        raise ValueError("No domain set in the initialization file.")
    if config["domain"] == "":
        raise ValueError("The domain is blank in the initialization file.")
    # set the catalog URL for your RegScale instance
    if host is None:
        url_login = normalize_url(config["domain"] + "/api/authentication/login")
    else:
        url_login = normalize_url(f"{host}/api/authentication/login")
    logger.info("Logging into: %s", url_login)

    # create object to authenticate
    auth = {"userName": str_user, "password": str_password, "oldPassword": ""}
    logging.debug(auth)
    if auth["password"]:
        try:
            user_id, token = regscale_login(url_login=url_login, auth=auth, app=app)

            # update init file from login
            config["token"] = token
            config["userId"] = user_id
            # write the changes back to file
            app.save_config(config)
            # set variables
            logger.info("User ID: %s", user_id)
            logger.info("New RegScale Token has been updated and saved in init.yaml")
            logger.debug("Token: %s", token)
        except TypeError as ex:
            logger.error("TypeError: %s", ex)
        except SSLCertVerificationError as sslex:
            logger.error(
                "SSLError, python requests requires a valid ssl certificate.\n%s", sslex
            )
            sys.exit(1)
    return token


def regscale_login(url_login: str, auth: dict, app) -> Tuple[str, str]:
    """
    Login to RegScale
    :param str url_login: RegScale URL to use for log in
    :param dict auth:
    :param app: Application object
    :raises: ConnectionError if unable to login user to RegScale
    :raises: JSONDecodeError if API response cannot be converted to a json object
    :return: Tuple[user id, JWT]
    :rtype: Tuple[str, str]
    """
    api = Api(app=app)
    try:
        # login and get token
        response = api.post(url=url_login, json=auth)
        if response.status_code == 200:
            auth_response = response.json()
            user_id = auth_response["id"]
            token = "Bearer " + auth_response["auth_token"]
        elif response.status_code == 400:
            logger.error("Invalid credentials were provided. Please try again.")
            sys.exit(1)
        else:
            logger.error(
                "Received unexpected response from RegScale.\n%s:%s",
                response.status_code,
                response.text,
            )
            sys.exit(1)
    except ConnectionError:
        logger.error(
            "ConnectionError: Unable to login user to RegScale, check the server domain."
        )
    except JSONDecodeError:
        logger.error(
            "Login Error: Unable to login user to instance: %s.", app.config["domain"]
        )
        sys.exit(1)
    return user_id, token


def is_valid(host=None, app=None) -> bool:
    """
    Quick endpoint to check login status
    :param host: host to verify login, defaults to None
    :param app: Application, defaults to None
    :raises: KeyError if token key not found in application config
    :raises: ConnectionError if unable to login user to RegScale
    :raises: JSONDecodeError if API response cannot be converted to a json object
    :return: Boolean if user is logged in or not
    :rtype: bool
    """
    config = app.config
    login_status = False
    api = Api(app=app)
    try:
        # Make sure url isn't default
        # login with token
        token = config["token"]
        headers = {"Authorization": token}
        if host is None:
            url_login = normalize_url(
                url=f'{config["domain"]}/api/logging/filterLogs/0/0'
            )
        else:
            url_login = normalize_url(url=f"{host}/api/logging/filterLogs/0/0")
        logger.debug("config: %s", config)
        logger.debug("is_valid url: %s", url_login)
        logger.debug("is_valid headers: %s", headers)
        if response := api.get(url=url_login, headers=headers):
            if response.status_code == 200:
                login_status = True
    except KeyError as ex:
        if str(ex).replace("'", "") == "token":
            logger.debug("Token is missing, we will generate this")
    except ConnectionError:
        logger.error(
            "ConnectionError: Unable to login user to RegScale, check the server domain."
        )
    except JSONDecodeError as decode_ex:
        logger.error(
            "Login Error: Unable to login user to RegScale instance:  %s.\n%s",
            config["domain"],
            decode_ex,
        )
    finally:
        logger.debug("login status: %s", login_status)
    return login_status


def is_licensed(app: Application) -> bool:
    """
    Verify if the application is licensed
    :param app: Application object
    :return: License status
    :rtype: bool
    """
    status = False
    api = Api(app=app)
    # TODO: Need to account for versions of the API with no license endpoint
    with contextlib.suppress(requests.RequestException):
        lic = app.get_regscale_license(appl=app, api=api).json()
        license_date = datetime.strptime(lic["expirationDate"], "%Y-%m-%d")
        if lic["licenseType"] == "Enterprise" and license_date > datetime.now():
            status = True
    return status
