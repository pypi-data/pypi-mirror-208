# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-04-24 15:36:07
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-04-24 16:28:13

CONNECTION_POINT_TAGS = {
    "ip-address": {
        "description": "Gather Interface's IP Address",
        "example": "10.10.10.121"
    },
    "mac-address": {
        "description": "Gather Interface's MAC Address",
        "example": "fa:16:3e:b7:48:f"
    },
    "vlan": {
        "description": "Gather Interface's VLAN ID",
        "example": 704
    },
    "type": {
        "description": "Gather Interface's Type",
        "example": "VIRTIO"
    },
    "name": {
        "description": "Gather Interface's Host Name",
        "example": "eth0"
    },
    "mgmt-interface": {
        "description": "Gather if the Interface is a mgmt interface",
        "example": True
    },
}