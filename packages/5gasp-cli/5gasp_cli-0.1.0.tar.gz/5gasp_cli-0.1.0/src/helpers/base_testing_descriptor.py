# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-04-26 09:33:16
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-04-26 10:01:15


BASE_TESTING_DESCRIPTOR = {
  "test_info": {
    "netapp_id": None,
    "network_service_id": None,
    "testbed_id": None,
    "description": None
  },
  "test_phases": {
    "setup": {
      "deployments": [],
      "testcases": []
    },
    "execution": [
      {
        "batch_id": 1,
        "scope": "predefined_tests",
        "executions": [
          {
            "execution_id": 1,
            "name": "predefined_test",
            "testcase_ids": None
          }
        ]
      }
    ]
  }
}