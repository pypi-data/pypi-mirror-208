#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" standard python imports """
from dataclasses import dataclass
from typing import Any


@dataclass
class Interconnects:
    """RegScale Interconnects dataclass"""

    id: int = 0
    uuid: str = ""
    name: str = ""
    organization: str = ""
    connectionType: str = ""
    authorizationType: str = ""
    agreementDate: str = ""
    expirationDate: str = ""
    categorization: str = ""
    status: str = ""
    ao: str = ""
    aoId: str = ""
    description: str = ""
    parentId: int = 0
    parentModule: str = ""
    createdBy: str = ""
    createdById: str = ""
    dateCreated: str = ""
    lastUpdatedBy: str = ""
    lastUpdatedById: str = ""
    dateLastUpdated: str = ""
    interconnectOwner: str = ""
    interconnectOwnerId: str = ""
    isPublic: bool = True

    @staticmethod
    def from_dict(obj: Any) -> "Interconnects":
        _id = int(obj.get("id"))
        _uuid = str(obj.get("uuid"))
        _name = str(obj.get("name"))
        _organization = str(obj.get("organization"))
        _connectionType = str(obj.get("connectionType"))
        _authorizationType = str(obj.get("authorizationType"))
        _agreementDate = str(obj.get("agreementDate"))
        _expirationDate = str(obj.get("expirationDate"))
        _categorization = str(obj.get("categorization"))
        _status = str(obj.get("status"))
        _ao = str(obj.get("ao"))
        _aoId = str(obj.get("aoId"))
        _description = str(obj.get("description"))
        _parentId = int(obj.get("parentId"))
        _parentModule = str(obj.get("parentModule"))
        _createdBy = str(obj.get("createdBy"))
        _createdById = str(obj.get("createdById"))
        _dateCreated = str(obj.get("dateCreated"))
        _lastUpdatedBy = str(obj.get("lastUpdatedBy"))
        _lastUpdatedById = str(obj.get("lastUpdatedById"))
        _dateLastUpdated = str(obj.get("dateLastUpdated"))
        _interconnectOwner = str(obj.get("interconnectOwner"))
        _interconnectOwnerId = str(obj.get("interconnectOwnerId"))
        _isPublic = True
        return Interconnects(
            _id,
            _uuid,
            _name,
            _organization,
            _connectionType,
            _authorizationType,
            _agreementDate,
            _expirationDate,
            _categorization,
            _status,
            _ao,
            _aoId,
            _description,
            _parentId,
            _parentModule,
            _createdBy,
            _createdById,
            _dateCreated,
            _lastUpdatedBy,
            _lastUpdatedById,
            _dateLastUpdated,
            _interconnectOwner,
            _interconnectOwnerId,
            _isPublic,
        )


# Example Usage
# jsonstring = json.loads(myjsonstring)
# Interconnects = Interconnects.from_dict(jsonstring)
