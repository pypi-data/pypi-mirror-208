#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for a RegScale Security Control Implementation """

# standard python imports
from dataclasses import asdict, dataclass, field
from typing import Any

from regscale.core.app.api import Api
from regscale.core.app.application import Application


@dataclass
class Control:
    """Control Model"""

    id: int = None
    isPublic: bool = True
    uuid: str = None
    controlId: str = None
    sortId: str = None
    controlType: str = None
    title: str = None
    description: str = None
    references: str = None
    relatedControls: str = None
    subControls: str = None
    enhancements: str = None
    family: str = None
    weight: int = None
    catalogueID: int = None
    archived: bool = False
    lastUpdatedById: str = None
    dateLastUpdated: str = None
    tenantsId: int = None

    @staticmethod
    def from_dict(obj: Any) -> "Control":
        """
        Create RegScale Control from dictionary
        :param obj: dictionary
        :return: Control class
        :rtype: Control
        """
        _id = int(obj.get("id", 0))
        _isPublic = bool(obj.get("isPublic"))
        _uuid = str(obj.get("uuid"))
        _controlId = str(obj.get("controlId"))
        _sortId = str(obj.get("sortId"))
        _controlType = str(obj.get("controlType"))
        _title = str(obj.get("title"))
        _description = str(obj.get("description"))
        _references = str(obj.get("references"))
        _relatedControls = str(obj.get("relatedControls"))
        _subControls = str(obj.get("subControls"))
        _enhancements = str(obj.get("enhancements"))
        _family = str(obj.get("family"))
        _weight = int(obj.get("weight", 0))
        _catalogueID = int(obj.get("catalogueID"))
        _archived = bool(obj.get("archived"))
        _lastUpdatedById = str(obj.get("lastUpdatedById"))
        _dateLastUpdated = str(obj.get("dateLastUpdated"))
        _tenantsId = int(obj.get("tenantsId"))
        return Control(
            _id,
            _isPublic,
            _uuid,
            _controlId,
            _sortId,
            _controlType,
            _title,
            _description,
            _references,
            _relatedControls,
            _subControls,
            _enhancements,
            _family,
            _weight,
            _catalogueID,
            _archived,
            _lastUpdatedById,
            _dateLastUpdated,
            _tenantsId,
        )

    def dict(self) -> dict:
        """
        Create a dictionary from the Control dataclass
        :return: Dictionary of Control
        :rtype: dict
        """
        return dict(asdict(self).items())


@dataclass(unsafe_hash=True)
class ControlImplementation:
    """Security Control Implementation model"""

    parentId: int = field(hash=True)  # Required
    parentModule: str = field(hash=True)  # Required
    controlOwnerId: str  # Required
    status: str = field(hash=True)  # Required
    controlID: int = field(hash=True)  # Required
    control: Control = None
    id: int = None
    createdById: str = None
    uuid: str = None
    policy: str = None
    implementation: str = None
    dateLastAssessed: str = None
    lastAssessmentResult: str = None
    practiceLevel: str = None
    processLevel: str = None
    cyberFunction: str = None
    implementationType: str = None
    implementationMethod: str = None
    qdWellDesigned: str = None
    qdProcedures: str = None
    qdSegregation: str = None
    qdFlowdown: str = None
    qdAutomated: str = None
    qdOverall: str = None
    qiResources: str = None
    qiMaturity: str = None
    qiReporting: str = None
    qiVendorCompliance: str = None
    qiIssues: str = None
    qiOverall: str = None
    responsibility: str = None
    inheritedControlId: int = None
    inheritedRequirementId: int = None
    inheritedSecurityPlanId: int = None
    inheritedPolicyId: int = None
    dateCreated: str = None
    lastUpdatedById: str = None
    dateLastUpdated: str = None
    weight: int = None
    isPublic: bool = True
    inheritable: bool = False

    @staticmethod
    def fetch_existing_implementations(
        app: Application, regscale_parent_id: int, regscale_module: str
    ):
        """_summary_

        :param app: Application instance
        :param regscale_parent_id: RegScale Parent ID
        :param regscale_module: RegScale Parent Module
        :return: _description_
        """
        api = Api(app)
        existing_implementations = []
        existing_implementations_response = api.get(
            url=app.config["domain"]
            + "/api/controlimplementation"
            + f"/getAllByParent/{regscale_parent_id}/{regscale_module}"
        )
        if existing_implementations_response.status_code == 200:
            existing_implementations = existing_implementations_response.json()
        return existing_implementations

    @staticmethod
    def from_dict(obj: Any) -> "ControlImplementation":
        """
        Create RegScale Security Control Implementation from dictionary
        :param obj: dictionary
        :return: ControlImplementation class
        :rtype: ControlImplementation
        """
        _id = int(obj.get("id")) if obj.get("id") else None
        _uuid = str(obj.get("uuid")) if obj.get("uuid") else None
        _control = Control.from_dict(obj.get("control"))
        _isPublic = bool(obj.get("isPublic")) if obj.get("isPublic") else None
        _inheritable = bool(obj.get("inheritable")) if obj.get("inheritable") else None
        _controlOwnerId = (
            str(obj.get("controlOwnerId")) if obj.get("controlOwnerId") else None
        )
        _policy = str(obj.get("policy")) if obj.get("policy") else None
        _implementation = (
            str(obj.get("implementation")) if obj.get("implementation") else None
        )
        _status = str(obj.get("status")) if obj.get("status") else None
        _dateLastAssessed = (
            str(obj.get("dateLastAssessed")) if obj.get("dateLastAssessed") else None
        )
        _lastAssessmentResult = (
            str(obj.get("lastAssessmentResult"))
            if obj.get("lastAssessmentResult")
            else None
        )
        _controlID = int(obj.get("controlID")) if obj.get("controlID") else None
        _practiceLevel = (
            str(obj.get("practiceLevel")) if obj.get("practiceLevel") else None
        )
        _processLevel = (
            str(obj.get("processLevel")) if obj.get("processLevel") else None
        )
        _cyberFunction = (
            str(obj.get("cyberFunction")) if obj.get("cyberFunction") else None
        )
        _implementationType = (
            str(obj.get("implementationType"))
            if obj.get("implementationType")
            else None
        )
        _implementationMethod = (
            str(obj.get("implementationMethod"))
            if obj.get("implementationMethod")
            else None
        )
        _qdWellDesigned = (
            str(obj.get("qdWellDesigned")) if obj.get("qdWellDesigned") else None
        )
        _qdProcedures = (
            str(obj.get("qdProcedures")) if obj.get("qdProcedures") else None
        )
        _qdSegregation = (
            str(obj.get("qdSegregation")) if obj.get("qdSegregation") else None
        )
        _qdFlowdown = str(obj.get("qdFlowdown")) if obj.get("qdFlowdown") else None
        _qdAutomated = str(obj.get("qdAutomated")) if obj.get("qdAutomated") else None
        _qdOverall = str(obj.get("qdOverall")) if obj.get("qdOverall") else None
        _qiResources = str(obj.get("qiResources")) if obj.get("qiResources") else None
        _qiMaturity = str(obj.get("qiMaturity")) if obj.get("qiMaturity") else None
        _qiReporting = str(obj.get("qiReporting")) if obj.get("qiReporting") else None
        _qiVendorCompliance = (
            str(obj.get("qiVendorCompliance"))
            if obj.get("qiVendorCompliance")
            else None
        )
        _qiIssues = str(obj.get("qiIssues")) if obj.get("qiIssues") else None
        _qiOverall = str(obj.get("qiOverall")) if obj.get("qiOverall") else None
        _responsibility = (
            str(obj.get("responsibility")) if obj.get("responsibility") else None
        )
        _inheritedControlId = (
            int(obj.get("inheritedControlId"))
            if obj.get("inheritedControlId")
            else None
        )
        _inheritedRequirementId = (
            int(obj.get("inheritedRequirementId"))
            if obj.get("inheritedRequirementId")
            else None
        )
        _inheritedSecurityPlanId = (
            int(obj.get("inheritedSecurityPlanId"))
            if obj.get("inheritedSecurityPlanId")
            else None
        )
        _inheritedPolicyId = (
            int(obj.get("inheritedPolicyId")) if obj.get("inheritedPolicyId") else None
        )
        _parentId = int(obj.get("parentId")) if obj.get("parentId") else None
        _parentModule = (
            str(obj.get("parentModule")) if obj.get("parentModule") else None
        )
        _createdById = str(obj.get("createdById")) if obj.get("createdById") else None
        _dateCreated = str(obj.get("dateCreated")) if obj.get("dateCreated") else None
        _lastUpdatedById = (
            str(obj.get("lastUpdatedById")) if obj.get("lastUpdatedById") else None
        )
        _dateLastUpdated = (
            str(obj.get("dateLastUpdated")) if obj.get("dateLastUpdated") else None
        )
        _weight = int(obj.get("weight")) if obj.get("weight") else None
        return ControlImplementation(
            _id,
            _uuid,
            _control,
            _isPublic,
            _inheritable,
            _controlOwnerId,
            _policy,
            _implementation,
            _status,
            _dateLastAssessed,
            _lastAssessmentResult,
            _controlID,
            _practiceLevel,
            _processLevel,
            _cyberFunction,
            _implementationType,
            _implementationMethod,
            _qdWellDesigned,
            _qdProcedures,
            _qdSegregation,
            _qdFlowdown,
            _qdAutomated,
            _qdOverall,
            _qiResources,
            _qiMaturity,
            _qiReporting,
            _qiVendorCompliance,
            _qiIssues,
            _qiOverall,
            _responsibility,
            _inheritedControlId,
            _inheritedRequirementId,
            _inheritedSecurityPlanId,
            _inheritedPolicyId,
            _parentId,
            _parentModule,
            _createdById,
            _dateCreated,
            _lastUpdatedById,
            _dateLastUpdated,
            _weight,
        )

    def dict(self) -> dict:
        """
        Create a dictionary from the Control Implementation dataclass
        :return: Dictionary of Control Implementation
        :rtype: dict
        """
        return dict(asdict(self).items())
