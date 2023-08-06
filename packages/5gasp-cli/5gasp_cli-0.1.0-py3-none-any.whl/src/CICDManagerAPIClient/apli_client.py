# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-04-06 14:55:17
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-05-15 17:40:28

import requests
from ..helpers import constants as Constants
from ..CICDManagerAPIClient.test_classes import Test


class CICDManagerAPIClient:
    def __init__(self):
        self.base_url = Constants.CI_CD_SERVICE_URL

    def get_all_testbeds(self):
        '''
        Retrieves  testbeds from the CI/CD Manager API.

        Returns
        -------
            List of testbeds.
        '''

        # 1. List only the testbeds that have tests
        response = self.__make_get_request(
            Constants.CI_CD_SERVICE_URL +
            Constants.CI_CD_SERVICE_URL_ENDPOINTS.ALL_TESTS.value
        )

        response_data = response.json()["data"]
        testbeds_with_tests = response_data["tests"].keys()

        # 2.Gather the testbeds description
        response = self.__make_get_request(
            Constants.CI_CD_SERVICE_URL +
            Constants.CI_CD_SERVICE_URL_ENDPOINTS.ALL_TESTBEDS.value
        )
        response_data = response.json()["data"]

        return [
            testbed
            for testbed
            in response_data["testbeds"]
            if testbed["id"] in testbeds_with_tests
        ]

    def get_all_tests(self):
        '''
        Retrieves all tests from the CI/CD Manager API.

        Returns
        -------
            List of all tests.
        '''
        path = Constants.ALL_TESTS_PATH
        url = f"{self.base_url}/{path}"

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
            return None
        except requests.exceptions.ConnectionError as errc:
            print(f"Connection Error: {errc}")
            return None
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Unknown Error: {err}")
            return None
        else:
            return response.json()['data']['tests']

    def get_tests_per_testbed(self, testbed: str):
        '''
        Retrieves all testbeds from the CI/CD Manager API.

        Parameters
        ----------
        testbed : str
            Testbed

        Returns
        -------
            List of all testbeds.
        '''
        response = self.__make_get_request(
            endpoint=Constants.CI_CD_SERVICE_URL +
            Constants.CI_CD_SERVICE_URL_ENDPOINTS.ALL_TESTS.value,
            params={"testbed": testbed}
        )

        tests = []
        for test_info in response.json()['data']['tests'][testbed].values():
            t = Test()
            t.load_from_dict(test_info)
            tests.append(t)

        return tests

    def __make_get_request(self, endpoint, params=None):
        try:
            response = requests.get(
                url=endpoint,
                params=params
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
            return None
        except requests.exceptions.ConnectionError as errc:
            print(f"Connection Error: {errc}")
            return None
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Unknown Error: {err}")
            return None
        else:
            return response
