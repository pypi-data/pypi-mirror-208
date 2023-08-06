#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for a RegScale Asset """

# standard python imports
from dataclasses import asdict, dataclass
from typing import Any, List

from requests import JSONDecodeError, Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application


@dataclass()
class Asset:
    """Asset Model"""

    name: str  # Required
    parentId: int  # Required
    parentModule: str  # Required
    isPublic: bool = True
    osVersion: str = None
    otherTrackingNumber: str = None
    serialNumber: str = None
    ipAddress: str = None
    macAddress: str = None
    manufacturer: str = None
    model: str = None
    assetCategory: str = None
    assetOwnerId: str = None
    operatingSystem: str = None
    osVersion: str = None
    assetType: str = None
    cmmcAssetType: str = None
    cpu: int = None
    ram: int = None
    diskStorage: int = None
    description: str = None
    endOfLifeDate: str = ""
    purchaseDate: str = ""
    status: str = None
    tenableId: str = None
    qualysId: str = None
    wizId: str = None
    wizInfo: str = None
    facilityId: int = None
    orgId: int = None
    id: int = None
    createdById: str = None
    lastUpdatedById: str = None
    fqdn: str = None
    notes: str = None
    securityPlanId: int = 0

    @staticmethod
    def from_dict(obj: dict) -> "Asset":
        """
        Create Asset object from dict
        :param obj: dictionary
        :return: Asset class
        :rtype: Asset
        """
        _osVersion = (
            str(obj.get("operatingSystemVersion"))
            if obj.get("operatingSystemVersion")
            else None
        )
        _isPublic = bool(obj.get("isPublic")) if obj.get("isPublic") else True
        _name = str(obj.get("name")) if obj.get("name") else None
        _otherTrackingNumber = (
            str(obj.get("otherTrackingNumber"))
            if obj.get("otherTrackingNumber")
            else None
        )
        _serialNumber = (
            str(obj.get("serialNumber")) if obj.get("serialNumber") else None
        )
        _ipAddress = str(obj.get("ipAddress")) if obj.get("ipAddress") else None
        _macAddress = (
            str(obj.get("macAddress")).upper() if obj.get("macAddress") else None
        )
        _manufacturer = (
            str(obj.get("manufacturer")) if obj.get("manufacturer") else None
        )
        _model = str(obj.get("model")) if obj.get("model") else None
        _assetCategory = (
            str(obj.get("assetCategory")) if obj.get("assetCategory") else None
        )
        _assetOwnerId = (
            str(obj.get("assetOwnerId")) if obj.get("assetOwnerId") else None
        )
        _operatingSystem = (
            str(obj.get("operatingSystem")) if obj.get("operatingSystem") else None
        )
        _osVersion = str(obj.get("osVersion")) if obj.get("osVersion") else None
        _assetType = str(obj.get("assetType")) if obj.get("assetType") else None
        _cmmcAssetType = (
            str(obj.get("cmmcAssetType")) if obj.get("cmmcAssetType") else None
        )
        _cpu = int(obj.get("cpu")) if obj.get("cpu") else 0
        _ram = int(obj.get("ram")) if obj.get("ram") else 0
        _diskStorage = int(obj.get("diskStorage")) if obj.get("diskStorage") else None
        _description = str(obj.get("description")) if obj.get("description") else None
        _endOfLifeDate = (
            str(obj.get("endOfLifeDate")) if obj.get("endOfLifeDate") else None
        )
        _purchaseDate = (
            str(obj.get("purchaseDate")) if obj.get("purchaseDate") else None
        )
        _fqdn = str(obj.get("fqdn"))
        _status = str(obj.get("status")) if obj.get("status") else None
        _tenableId = str(obj.get("tenableId")) if obj.get("tenableId") else None
        _qualysId = str(obj.get("qualysId")) if obj.get("qualysId") else None
        _wizId = str(obj.get("wizId")) if obj.get("wizId") else None
        _wizInfo = str(obj.get("wizInfo")) if obj.get("wizInfo") else None
        if obj.get("facilityId"):
            _facilityId = int(obj.get("facilityId"))
        else:
            _facilityId = None
        if obj.get("orgId"):
            _orgId = int(obj.get("orgId"))
        else:
            _orgId = None
        _parentId = int(obj.get("parentId"))
        _parentModule = str(obj.get("parentModule"))
        if obj.get("id"):
            _id = obj.get("id")
        else:
            _id = None
        _notes = str(obj.get("notes")) if obj.get("notes") else ""
        _securityPlanId = (
            int(obj.get("securityPlanId")) if obj.get("securityPlanId") else 0
        )
        return Asset(
            isPublic=_isPublic,
            name=_name,
            otherTrackingNumber=_otherTrackingNumber,
            serialNumber=_serialNumber,
            ipAddress=_ipAddress,
            macAddress=_macAddress.upper() if _macAddress else None,
            manufacturer=_manufacturer,
            model=_model,
            assetOwnerId=_assetOwnerId,
            operatingSystem=_operatingSystem,
            osVersion=_osVersion,
            assetCategory=_assetCategory,
            assetType=_assetType,
            cmmcAssetType=_cmmcAssetType,
            cpu=_cpu,
            ram=_ram,
            diskStorage=_diskStorage,
            description=_description,
            endOfLifeDate=_endOfLifeDate,
            purchaseDate=_purchaseDate,
            status=_status,
            tenableId=_tenableId,
            qualysId=_qualysId,
            wizId=_wizId,
            wizInfo=_wizInfo,
            facilityId=_facilityId,
            orgId=_orgId,
            parentId=_parentId,
            parentModule=_parentModule,
            id=_id,
            fqdn=_fqdn,
            notes=_notes,
            securityPlanId=_securityPlanId,
        )

    # 'uniqueness': 'ip, macaddress'
    # Enable object to be hashable
    def __hash__(self):
        """
        Enable object to be hashable
        :return: Hashed TenableAsset
        """
        return hash(
            (
                self.name,
                self.ipAddress,
                self.macAddress.lower() if self.macAddress else None,
                self.assetCategory,
                self.assetType,
                self.fqdn,
                self.parentId,
                self.parentModule,
                self.description,
                self.notes,
            )
        )

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

    def __eq__(self, other) -> "Asset":
        """
        Update items in TenableAsset class
        :param other:
        :return: Updated Asset
        :rtype: Asset
        """
        return (
            self.name == other.name
            and self.ipAddress == other.ipAddress
            and self.macAddress == other.macAddress
            and self.wizId == other.wizId
            and self.description == other.description
            and self.notes == other.notes
        )

    def dict(self) -> dict:
        """
        Create a dictionary from the Asset dataclass
        :return: Dictionary of Asset
        :rtype: dict
        """
        return {k: v for k, v in asdict(self).items()}

    @staticmethod
    def insert_asset(
        app: Application,
        obj: Any,
    ) -> Response:
        """
        Create an asset in RegScale via API
        :param app: Application Instance
        :param obj: Asset Object
        :return: Response from RegScale after inserting the provided asset object
        :rtype: Response
        """
        if isinstance(obj, Asset):
            obj = asdict(obj)
        api = Api(app)
        res = api.post(url=app.config["domain"] + "/api/assets", json=obj)
        return res

    @staticmethod
    def find_assets_by_parent(
        app: Application,
        parent_id: int,
        parent_module: str,
    ) -> List["Asset"]:
        """
        Find all assets by parent id and parent module
        :param app: Application Instance
        :param parent_id: Parent Id
        :param parent_module: Parent Module
        :return: List of Assets
        :rtype: List[Asset]
        """
        api = Api(app)
        try:
            res = api.get(
                url=app.config["domain"]
                + f"/api/assets/getAllByParent/{parent_id}/{parent_module}"
            )
            existing_assets = res.json()
        except JSONDecodeError:
            existing_assets = []
        existing_assets = [Asset.from_dict(asset) for asset in existing_assets]
        return existing_assets
