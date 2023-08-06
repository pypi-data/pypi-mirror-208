#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for a RegScale Ports and Protocols """
from typing import Any


class PortsProtocols:
    """Ports And Protocols"""

    parentId: int
    parentModule: str
    startPort: int
    endPort: int
    protocol: str
    service: str
    purpose: str
    used_by: str
    createdById: str
    lastUpdatedById: str

    def __init__(
        self,
        parentId: int,
        parentModule: str,
        startPort: int,
        endPort: int,
        protocol: str,
        service: str,
        purpose: str,
        usedBy: str,
        createdById: str,
        lastUpdatedById: str,
    ) -> None:
        self.parentId = parentId
        self.parentModule = parentModule
        self.startPort = startPort
        self.endPort = endPort
        self.protocol = protocol
        self.service = service
        self.purpose = purpose
        self.used_by = usedBy
        self.createdById = createdById
        self.lastUpdatedById = lastUpdatedById

    def __hash__(self):
        return hash(
            (
                self.parentId,
                self.parentModule,
                self.startPort,
                self.endPort,
                self.protocol,
                self.service,
                self.purpose,
            )
        )

    @staticmethod
    def from_dict(obj: Any) -> "PortsProtocols":
        """
        Create RegScale Port and Protocol from dictionary
        :param obj: dictionary
        :return: ControlImplementation class
        :rtype: ControlImplementation
        """
        if "id" in obj:
            del obj["id"]
        _parent_id = int(obj.get("parentId"))
        _parent_module = obj.get("parentModule")
        _start_port = obj.get("startPort")
        _end_port = obj.get("endPort")
        _protocol = obj.get("protocol")
        _service = obj.get("service")
        _purpose = obj.get("purpose")
        _used_by = obj.get("used_by")
        _created_by_id = obj.get("created_by_id")
        _last_updated_by_id = obj.get("last_updated_by_id")
        return PortsProtocols(
            _parent_id,
            _parent_module,
            _start_port,
            _end_port,
            _protocol,
            _service,
            _purpose,
            _used_by,
            _created_by_id,
            _last_updated_by_id,
        )
