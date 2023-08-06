# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-02-18 15:26:20
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-04-26 23:35:08

import yaml
from typing import List


class ConnectionPointsParser:
    """
    Injected Tags Parser Class
    """
    validated_connection_points = None
    _interfaces = None

    def __init__(self, nsd_filepaths: List[str]):
        """
        Constructor
        """
        self.base_nsd_filepaths = set(nsd_filepaths)
        self.validated_connection_points = {}
        self._interfaces = []
        self.infer_connection_points()

    def infer_connection_points(self):
        for filepath in self.base_nsd_filepaths:
            self.parse_descriptor(filepath)

    def parse_descriptor(self, nsd_filepath):
        '''
        Retrieves all the tags from the given descriptor
        '''
        try:
            connection_points = []

            with open(nsd_filepath, "r") as file:
                descriptor = yaml.safe_load(file)

            for network_service in descriptor['nsd']['nsd']:
                ns_id = network_service['id']
                for df in network_service['df']:
                    connection_points += self.infer_connection_points_from_df(
                        ns_id=ns_id,
                        df=df,
                    )
            # save connection points
            self.validated_connection_points[nsd_filepath] = {
                "ns_id": ns_id,
                "connection_points": connection_points
            }

        except Exception as e:
            print("\nThe following exception occurred when trying to infer " +
                  f"connection points for the NSD '{nsd_filepath}': {e}.")

    def infer_connection_points_from_df(self, ns_id, df):
        connection_points = []
        for vnf in df['vnf-profile']:
            vnf_id = vnf['id']
            for constituent in vnf['virtual-link-connectivity']:
                for constituent_cpd in constituent["constituent-cpd-id"]:
                    interface_id = constituent_cpd['constituent-cpd-id']
                    connection_points.append(
                        "{{" + f"{ns_id}|{vnf_id}|{interface_id}" + "}}"
                    )
        return connection_points

    @property
    def connection_points(self):
        '''
        Get interfaces
        '''
        return self.validated_connection_points
