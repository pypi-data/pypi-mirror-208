#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" standard python imports """

from dataclasses import dataclass
from typing import Any

import requests

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import create_logger, get_current_datetime
from regscale.models.regscale_models.objective import Objective


@dataclass
class ImplementationOption(Objective):
    """RegScale Implementation Option"""

    name: str  # Required
    description: str  # Required
    acceptability: str
    otherId: str
    securityControlId: int
    objectiveId: int
    createdById: str = None
    lastUpdatedById: str = None
    dateCreated: str = get_current_datetime()
    dateLastUpdated: str = get_current_datetime()
    archived: bool = False

    @staticmethod
    def from_dict(obj: Any) -> "ImplementationOption":
        """
        Create Implementation Option object from a Dictionary
        :param Any obj: dictionary of an Implementation Option
        :return: RegScale implementation objective
        :rtype: ImplementationOption
        """

        _id = int(obj.get("id"))
        _uuid = str(obj.get("uuid"))
        _name = str(obj.get("name"))
        _description = str(obj.get("description"))
        _acceptability = str(obj.get("acceptability"))
        _otherId = int(obj.get("otherId"))
        _implementationId = int(obj.get("implementationId"))
        _securityControlId = int(obj.get("securityControlId"))
        _objectiveId = int(obj.get("objectiveId"))
        _createdById = str(obj.get("createdById"))
        _dateCreated = str(obj.get("dateCreated"))
        _lastUpdatedById = str(obj.get("lastUpdatedById"))
        _dateLastUpdated = str(obj.get("dateLastUpdated"))
        return ImplementationOption(
            _id,
            _uuid,
            _name,
            _description,
            _acceptability,
            _otherId,
            _implementationId,
            _securityControlId,
            _objectiveId,
            _createdById,
            _dateCreated,
            _lastUpdatedById,
            _dateLastUpdated,
        )

    @staticmethod
    def fetch_implementation_options(app: Application, control_id: int) -> list[dict]:
        """
        Fetch list of implementation objectives by control id
        :param Application app: Application Instance
        :param int control_id: Security Control ID
        :return: A list of Implementation Objectives as a dictionary from RegScale via API
        :rtype: list[dict]
        """
        results = []
        logger = create_logger()
        api = Api(app)
        res = api.get(
            url=app.config["domain"]
            + f"/api/implementationoptions/getByControl/{control_id}"
        )
        if res.ok:
            try:
                results = res.json()
            except requests.RequestException.JSONDecodeError:
                logger.warning("Unable to find control implementation objectives.")
        return results
