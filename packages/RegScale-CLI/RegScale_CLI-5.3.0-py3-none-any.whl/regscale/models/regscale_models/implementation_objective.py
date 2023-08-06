#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" standard python imports """

from dataclasses import asdict, dataclass
from enum import Enum
from logging import Logger
from typing import Any

import requests
from requests import Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.objective import Objective


class ImplementationStatus(Enum):
    """
    Implementation Status
    :param Enum: Enum
    """

    FULLY_IMPLEMENTED = "Fully Implemented"
    PARTIALLY_IMPLEMENTED = "Partially Implemented"
    NOT_IMPLEMENTED = "Not Implemented"


@dataclass
class ImplementationObjective(Objective):
    """RegScale Implementation Objective"""

    notes: str  # Required
    status: str  # Required
    implementationId: int  # Required
    optionId: int  # Required
    objectiveId: int = None
    createdById: str = None
    lastUpdatedById: str = None
    dateLastAssessed: str = get_current_datetime()
    dateCreated: str = get_current_datetime()
    dateLastUpdated: str = get_current_datetime()

    @property
    def logger(self) -> Logger:
        """
        Logger implementation for a dataclass
        :return: logger object
        :rtype: Logger
        """
        logger = create_logger()
        return logger

    @staticmethod
    def from_dict(obj: Any) -> "ImplementationObjective":
        """
        Implementation Objective to Dictionary
        :param Any obj: Implementation Objective
        :return: RegScale implementation objective
        :rtype: ImplementationObjective
        """
        _id = int(obj.get("id", 0)) or None
        _uuid = str(obj.get("uuid"))
        _notes = str(obj.get("notes"))
        _status = str(obj.get("status"))
        _dateLastAssessed = str(obj.get("dateLastAssessed"))
        _optionId = int(obj.get("optionId", 0))
        _implementationId = int(obj.get("implementationId", 0))
        _securityControlId = int(obj.get("securityControlId", 0))
        _objectiveId = int(obj.get("objectiveId", 0))
        return ImplementationObjective(
            _securityControlId,
            _id,
            _uuid,
            _notes,
            _status,
            _implementationId,
            _optionId,
            _objectiveId,
            _dateLastAssessed,
        )

    @staticmethod
    def fetch_all(
        app: Application,
    ) -> list[dict]:
        """
        Fetch list of all implementation objectives in RegScale via API
        :param Application app: Application Instance
        :return: A list of Implementation Objectives as a list of dictionaries
        :rtype: list[dict]
        """
        results = []
        logger = create_logger()
        api = Api(app)
        res = api.get(url=app.config["domain"] + "/api/implementationObjectives")
        if res.ok:
            try:
                results = res.json()
            except requests.exceptions.JSONDecodeError:
                logger.warning("Unable to find control implementation objectives.")
        return results

    @staticmethod
    def update_objective(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Update a single implementation objective
        :param Application app: Application Instance
        :param Any obj: Implementation Objective
        :return: Response from RegScale API
        :rtype: Response
        """
        if isinstance(obj, ImplementationObjective):
            obj = asdict(obj)
        api = Api(app=app, retry=10)
        res = api.put(
            url=app.config["domain"] + f"/api/implementationObjectives/{obj['id']}",
            json=obj,
        )
        return res

    @staticmethod
    def insert_objective(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Update a single implementation objective
        :param Application app: Application Instance
        :param Any obj: Implementation Objective
        :return: Response from RegScale API
        :rtype: Response
        """
        if isinstance(obj, ImplementationObjective):
            obj = asdict(obj)
        api = Api(app=app, retry=10)
        res = api.post(
            url=app.config["domain"] + "/api/implementationObjectives", json=obj
        )
        return res

    @staticmethod
    def fetch_implementation_objectives(
        app: Application, control_id: int, query_type="implementation"
    ) -> list[dict]:
        """
        Fetch list of implementation objectives by control id
        :param Application app: Application Instance
        :param int control_id: Implementation Control ID
        :param str query_type: Query Type for GraphQL query
        :return: A list of Implementation Objectives as a dictionary
        """
        graph_query = """
                        query {
                        implementationObjectives (skip: 0, take: 50,  where: {securityControlId: {eq: placeholder}}) {
                            items {
                                    id
                                    notes
                                    optionId
                                    objectiveId
                                    implementationId
                                    securityControlId
                                    status
                            }
                            totalCount
                                pageInfo {
                                    hasNextPage
                                }
                        }
                    }
                        """.replace(
            "placeholder", str(control_id)
        )
        results = []
        logger = create_logger()
        api = Api(app)
        if query_type != "implementation":
            results = api.graph(graph_query)
        else:
            res = api.get(
                url=app.config["domain"]
                + f"/api/implementationObjectives/getByControl/{control_id}"
            )
            if res.ok:
                try:
                    results = res.json()
                except requests.exceptions.JSONDecodeError:
                    logger.warning("Unable to find control implementation objectives.")
        return results
