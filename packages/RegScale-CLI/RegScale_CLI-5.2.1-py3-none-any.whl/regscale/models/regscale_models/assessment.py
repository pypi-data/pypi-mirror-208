#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for a RegScale Assessment """
from dataclasses import asdict, dataclass


@dataclass
class Assessment:
    """Assessment Model"""

    leadAssessorId: str  # Required field
    title: str  # Required field
    assessmentType: str  # Required field
    plannedStart: str  # Required field
    plannedFinish: str  # Required field
    status: str = "Scheduled"  # Required field
    id: int = None
    facilityId: int = None
    orgId: int = None
    assessmentResult: str = ""
    actualFinish: str = ""
    assessmentReport: str = None
    masterId: int = None
    complianceScore: float = None
    targets: str = None
    automationInfo: str = None
    automationId: str = None
    metadata: str = None
    assessmentPlan: str = None
    oscalsspId: int = None
    oscalComponentId: int = None
    controlId: int = None
    requirementId: int = None
    securityPlanId: int = None
    projectId: int = None
    supplyChainId: int = None
    policyId: int = None
    componentId: int = None
    incidentId: int = None
    parentId: int = None
    parentModule: str = None
    createdById: str = None
    dateCreated: str = None
    lastUpdatedById: str = None
    dateLastUpdated: str = None
    isPublic: bool = True

    def __getitem__(self, key: any) -> any:
        """
        Get attribute from Pipeline
        :param any key:
        :return: value of provided key
        :rtype: any
        """
        return getattr(self, key)

    def __setitem__(self, key: any, value: any) -> None:
        """
        Set attribute in Pipeline with provided key
        :param any key: Key to change to provided value
        :param any value: New value for provided Key
        :return: None
        """
        return setattr(self, key, value)

    def dict(self) -> dict:
        """
        Create a dictionary from the Assessment dataclass
        :return: Dictionary of Assessment
        :rtype: dict
        """
        return {k: v for k, v in asdict(self).items()}

    @staticmethod
    def from_dict(obj: dict) -> "Assessment":
        """
        Create Assessment object from dict
        :param obj: dictionary
        :return: Assessment class
        :rtype: Assessment
        """
        _leadAssessorId = str(obj.get("leadAssessorId"))
        _title = str(obj.get("title"))
        _assessmentType = str(obj.get("assessmentType"))
        _plannedStart = str(obj.get("plannedStart"))
        _plannedFinish = str(obj.get("plannedFinish"))
        _status = str(obj.get("status"))
        _assessmentResult = str(obj.get("assessmentResult"))
        _actualFinish = str(obj.get("actualFinish"))
        _assessmentReport = str(obj.get("assessmentReport"))
        _complianceScore = float(obj.get("complianceScore"))
        _targets = str(obj.get("targets"))
        _automationInfo = str(obj.get("automationInfo"))
        _metadata = str(obj.get("metadata"))
        _assessmentPlan = str(obj.get("assessmentPlan"))
        _parentModule = str(obj.get("parentModule"))
        _createdById = str(obj.get("createdById"))
        _dateCreated = str(obj.get("dateCreated"))
        _lastUpdatedById = str(obj.get("lastUpdatedById"))
        _dateLastUpdated = str(obj.get("dateLastUpdated"))
        _isPublic = bool(obj.get("isPublic"))
        _facilityId = int(obj.get("facilityId", 0)) or None
        _orgId = int(obj.get("orgId", 0)) or None
        if obj.get("id"):
            _id = int(obj.get("id"))
        else:
            _id = None
        if obj.get("masterId"):
            _masterId = int(obj.get("masterId"))
        else:
            _masterId = None
        if obj.get("orgId"):
            _automationId = int(obj.get("automationId"))
        else:
            _automationId = None
        if obj.get("oscalsspId"):
            _oscalsspId = int(obj.get("oscalsspId"))
        else:
            _oscalsspId = None
        if obj.get("oscalComponentId"):
            _oscalComponentId = int(obj.get("oscalComponentId"))
        else:
            _oscalComponentId = None
        if obj.get("controlId"):
            _controlId = int(obj.get("controlId"))
        else:
            _controlId = None
        if obj.get("requirementId"):
            _requirementId = int(obj.get("requirementId"))
        else:
            _requirementId = None
        if obj.get("securityPlanId"):
            _securityPlanId = int(obj.get("securityPlanId"))
        else:
            _securityPlanId = None
        if obj.get("projectId"):
            _projectId = int(obj.get("projectId"))
        else:
            _projectId = None
        if obj.get("supplyChainId"):
            _supplyChainId = int(obj.get("supplyChainId"))
        else:
            _supplyChainId = None
        if obj.get("policyId"):
            _policyId = int(obj.get("policyId"))
        else:
            _policyId = None
        if obj.get("componentId"):
            _componentId = int(obj.get("componentId"))
        else:
            _componentId = None
        if obj.get("incidentId"):
            _incidentId = int(obj.get("incidentId"))
        else:
            _incidentId = None
        if obj.get("parentId"):
            _parentId = int(obj.get("parentId"))
        else:
            _parentId = None

        return Assessment(
            leadAssessorId=_leadAssessorId,
            title=_title,
            assessmentType=_assessmentType,
            plannedStart=_plannedStart,
            plannedFinish=_plannedFinish,
            status=_status,
            id=_id,
            facilityId=_facilityId,
            orgId=_orgId,
            assessmentResult=_assessmentResult,
            actualFinish=_actualFinish,
            assessmentReport=_assessmentReport,
            masterId=_masterId,
            complianceScore=_complianceScore,
            targets=_targets,
            automationInfo=_automationInfo,
            automationId=_automationId,
            metadata=_metadata,
            assessmentPlan=_assessmentPlan,
            oscalsspId=_oscalsspId,
            oscalComponentId=_oscalComponentId,
            controlId=_controlId,
            requirementId=_requirementId,
            securityPlanId=_securityPlanId,
            projectId=_projectId,
            supplyChainId=_supplyChainId,
            policyId=_policyId,
            componentId=_componentId,
            incidentId=_incidentId,
            parentId=_parentId,
            parentModule=_parentModule,
            createdById=_createdById,
            dateCreated=_dateCreated,
            lastUpdatedById=_lastUpdatedById,
            dateLastUpdated=_dateLastUpdated,
            isPublic=_isPublic,
        )
