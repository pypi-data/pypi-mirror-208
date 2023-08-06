#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python Standard Imports """
import json
from dataclasses import dataclass
from typing import Any


@dataclass
class SecurityPlan:
    """Security Plan

    :return: _description_
    """

    systemName: str  # Required
    planInformationSystemSecurityOfficerId: str  # Required
    planAuthorizingOfficialId: str  # Required
    systemOwnerId: str = ""
    otherIdentifier: str = ""
    confidentiality: str = ""
    integrity: str = ""
    availability: str = ""
    status: str = ""
    description: str = ""
    dateSubmitted: str = ""
    approvalDate: str = ""
    expirationDate: str = ""
    systemType: str = ""
    purpose: str = ""
    conditionsOfApproval: str = ""
    environment: str = ""
    lawsAndRegulations: str = ""
    authorizationBoundary: str = ""
    networkArchitecture: str = ""
    dataFlow: str = ""
    overallCategorization: str = ""
    maturityTier: str = ""
    wizProjectId: str = ""
    serviceNowAssignmentGroup: str = ""
    jiraProject: str = ""
    tenableGroup: str = ""
    facilityId: int = None
    orgId: int = None
    parentId: int = 0
    parentModule: str = ""
    createdById: str = ""
    dateCreated: str = ""
    lastUpdatedById: str = ""
    dateLastUpdated: str = ""
    users: int = 0
    privilegedUsers: int = 0
    usersMFA: int = 0
    privilegedUsersMFA: int = 0
    hva: bool = False
    practiceLevel: str = ""
    processLevel: str = ""
    cmmcLevel: str = ""
    cmmcStatus: str = ""
    isPublic: bool = True
    executiveSummary: str = ""
    recommendations: str = ""
    id: int = None
    uuid: str = ""

    @staticmethod
    def from_dict(obj: Any) -> "SecurityPlan":
        _id = int(obj.get("id"))
        _uuid = str(obj.get("uuid"))
        _systemName = str(obj.get("systemName"))
        _planInformationSystemSecurityOfficerId = str(
            obj.get("planInformationSystemSecurityOfficerId")
        )
        _planAuthorizingOfficialId = str(obj.get("planAuthorizingOfficialId"))
        _systemOwnerId = str(obj.get("systemOwnerId"))
        _otherIdentifier = str(obj.get("otherIdentifier"))
        _confidentiality = str(obj.get("confidentiality"))
        _integrity = str(obj.get("integrity"))
        _availability = str(obj.get("availability"))
        _status = str(obj.get("status"))
        _description = str(obj.get("description"))
        _dateSubmitted = str(obj.get("dateSubmitted"))
        _approvalDate = str(obj.get("approvalDate"))
        _expirationDate = str(obj.get("expirationDate"))
        _systemType = str(obj.get("systemType"))
        _purpose = str(obj.get("purpose"))
        _conditionsOfApproval = str(obj.get("conditionsOfApproval"))
        _environment = str(obj.get("environment"))
        _lawsAndRegulations = str(obj.get("lawsAndRegulations"))
        _authorizationBoundary = str(obj.get("authorizationBoundary"))
        _networkArchitecture = str(obj.get("networkArchitecture"))
        _dataFlow = str(obj.get("dataFlow"))
        _overallCategorization = str(obj.get("overallCategorization"))
        _maturityTier = str(obj.get("maturityTier"))
        _wizProjectId = str(obj.get("wizProjectId"))
        _serviceNowAssignmentGroup = str(obj.get("serviceNowAssignmentGroup"))
        _jiraProject = str(obj.get("jiraProject"))
        _tenableGroup = str(obj.get("tenableGroup"))
        _facilityId = int(obj.get("facilityId"))
        _orgId = int(obj.get("orgId"))
        _parentId = int(obj.get("parentId"))
        _parentModule = str(obj.get("parentModule"))
        _createdById = str(obj.get("createdById"))
        _dateCreated = str(obj.get("dateCreated"))
        _lastUpdatedById = str(obj.get("lastUpdatedById"))
        _dateLastUpdated = str(obj.get("dateLastUpdated"))
        _users = int(obj.get("users"))
        _privilegedUsers = int(obj.get("privilegedUsers"))
        _usersMFA = int(obj.get("usersMFA"))
        _privilegedUsersMFA = int(obj.get("privilegedUsersMFA"))
        _hva = obj.get("hva")
        _practiceLevel = str(obj.get("practiceLevel"))
        _processLevel = str(obj.get("processLevel"))
        _cmmcLevel = str(obj.get("cmmcLevel"))
        _cmmcStatus = str(obj.get("cmmcStatus"))
        _isPublic = obj.get("isPublic")
        _executiveSummary = str(obj.get("executiveSummary"))
        _recommendations = str(obj.get("recommendations"))
        return SecurityPlan(
            _id,
            _uuid,
            _systemName,
            _planInformationSystemSecurityOfficerId,
            _planAuthorizingOfficialId,
            _systemOwnerId,
            _otherIdentifier,
            _confidentiality,
            _integrity,
            _availability,
            _status,
            _description,
            _dateSubmitted,
            _approvalDate,
            _expirationDate,
            _systemType,
            _purpose,
            _conditionsOfApproval,
            _environment,
            _lawsAndRegulations,
            _authorizationBoundary,
            _networkArchitecture,
            _dataFlow,
            _overallCategorization,
            _maturityTier,
            _wizProjectId,
            _serviceNowAssignmentGroup,
            _jiraProject,
            _tenableGroup,
            _facilityId,
            _orgId,
            _parentId,
            _parentModule,
            _createdById,
            _dateCreated,
            _lastUpdatedById,
            _dateLastUpdated,
            _users,
            _privilegedUsers,
            _usersMFA,
            _privilegedUsersMFA,
            _hva,
            _practiceLevel,
            _processLevel,
            _cmmcLevel,
            _cmmcStatus,
            _isPublic,
            _executiveSummary,
            _recommendations,
        )


# Example Usage
# jsonstring = json.loads(myjsonstring)
# SecurityPlan = SecurityPlan.from_dict(jsonstring)
