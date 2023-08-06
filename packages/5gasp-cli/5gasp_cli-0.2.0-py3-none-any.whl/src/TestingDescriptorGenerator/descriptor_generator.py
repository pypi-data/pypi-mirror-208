# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-04-03 23:41:36
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-05-15 18:12:08

# OS
import os
from ..helpers.beatiful_prints import PrintAsTable, PrintAsPanelColumns
from ..helpers import prompts
import yaml

from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm
from rich.text import Text
from rich.console import Console
from ..CICDManagerAPIClient.test_classes import TestCase
from ..helpers.connection_point_tags import CONNECTION_POINT_TAGS
from ..helpers.base_testing_descriptor import BASE_TESTING_DESCRIPTOR


class TestingDescriptorGenerator:
    def __init__(self, netapp_name, ns_name, testbed_id, tests,
                 output_filepath, connection_points=None):
        self.netapp_name = netapp_name
        self.ns_name = ns_name
        self.testbed_id = testbed_id
        self.tests = tests
        self.output_filepath = output_filepath
        self.connection_points = connection_points
        self.test_cases = []
        self.tests_cases_ids_ordered_by_user = []
        self.last_test_id = 1

    def _show_test_info(self):
        test_id = Prompt.ask(
                "For which test do you wish to see additional information? ",
                choices=[str(i) for i in range(1, len(self.tests)+1)]
            )
        panels = PrintAsPanelColumns(
                panels=[self.tests[int(test_id)-1].to_panel(expand=True)]
            )
        panels.print()

    def __test_variable_input(self, test_variable):
        value = None
        prompt = "Which value would you like to assign to the variable "\
            f"'{test_variable.name}'?"

        if test_variable.can_be_injected_by_the_nods and self.connection_points:

            connection_points = []
            connection_point_keys = list(CONNECTION_POINT_TAGS.keys())

            for cps in self.connection_points.values():
                connection_points += cps["connection_points"]

            # Prepare table printing
            tmp_smaller_list = connection_points \
                if len(connection_points) < len(connection_point_keys) \
                else connection_point_keys
            diff = abs(len(connection_points) - len(connection_point_keys))
            tmp_smaller_list += [" "]*diff

            # Print Connection Points
            panels = PrintAsTable(
                header=["Connection Points", "Connection Point Keys"],
                rows=[
                    [connection_points[i], connection_point_keys[i]]
                    for i
                    in range(len(connection_points))
                ]
            )
            panels.print()

        # Ask for user's input
        # If there are possible values, ask for one of them
        if len(test_variable.possible_options) != 0:
            value = Prompt.ask(prompt, choices=test_variable.possible_options)
        elif test_variable.type == "str":
            value = Prompt.ask(prompt)
        elif test_variable.type == "float":
            value = FloatPrompt.ask(prompt)
        elif test_variable.type == "int":
            value = IntPrompt.ask(prompt)

        console = Console()
        variable_value_text = Text(f"{test_variable.name} = {value}\n",
                                   style="red")
        console.print(variable_value_text)
        return value

    def _add_test(self):
        console = Console()

        test_id = Prompt.ask(
                "Which test do you want to add to your Testing Descriptor? ",
                choices=[str(i) for i in range(1, len(self.tests)+1)]
            )
        test_id = int(test_id) - 1

        test = self.tests[test_id]

        test_info = Text()
        test_info.append(f"Configuring test '{test.name}'...\n", style="bold")
        test_info.append("Test name: ", style="bold")
        test_info.append(test.name + "\n")
        test_info.append("Test Description: ", style="bold")
        test_info.append(test.description + "\n")
        test_info.append("\nConfiguring Test Variables...\n", style="bold")
        console.print(test_info)

        test_id = int(test_id) - 1

        # Save Test Case Definition
        test_case = TestCase(test=test, test_case_id=self.last_test_id)

        for test_variable in test.test_variables:
            console.print(
                test_variable.to_panel(test.name)
            )

            if test_variable.can_be_injected_by_the_nods and self.connection_points:
                text = Text("This variable can be injected by the " +
                            "NODS. You may rely on the inferred " +
                            "connection points..", style="bold")
                console.print(text)
            
            else:
                text = Text("This variable can be injected by the " +
                            "NODS, but no NSD was passed. You can inject the" +
                            " values mannualy, or you can pass a descriptor" + 
                            " to the CLI.", style="bold")
                console.print(text)

            value = self.__test_variable_input(test_variable)
            # Save Test Case Definition
            test_case.add_test_variable(
                key=test_variable.name,
                value=value
            )

        description = Prompt.ask("How would you describe this Test Case")
        test_case.description = description

        console.print(test_case.to_panel(show_configured=True))
        self.test_cases.append(test_case)
        self.last_test_id += 1

    def _show_test_cases(self):
        # Print Header
        console = Console()
        header = Text("\nYou already configured the following Test Cases:",
                      style="bold")
        console.print(header)
        # Print all configured Test Cases
        panels = [tc.to_panel(expand=False) for tc in self.test_cases]
        panel_columns = PrintAsPanelColumns(panels)
        panel_columns.print()

    def _finish_test_cases_definition(self):
        console = Console()
        info = Text("\nYou have finished the Test Cases Definition.\n")
        info.append("You can now choose if your Test Cases should be " +
                    "executed in a specific order, or if the execution " +
                    "order is irrelevant.", style="bold")
        console.print(info)

        execution_order_is_required = Confirm.ask(
            "\nDo you wish to execute the defined Test Cases in a specific " +
            "order?"
            )

        if execution_order_is_required:
            self._set_tests_execution_order()
        else:
            self.tests_cases_ids_ordered_by_user = [
                tc.test_case_id
                for tc
                in self.test_cases
            ]

    def _set_tests_execution_order(self):
        self._show_test_cases()

        # Print Header
        console = Console()
        header = Text("\nYou can now define the execution order of the " +
                      "configured Test Cases.\nTo do so, please keep " +
                      "choosing the next test that shall be executed, until " +
                      "you have chosen all Test Cases.", style="bold"
                      )
        console.print(header)

        # Initial Test Cases IDs
        test_cases_ids = sorted([tc.test_case_id for tc in self.test_cases])
        tests_cases_ids_ordered_by_user = []
        while len(test_cases_ids) > 0:
            test_case_id = Prompt.ask(
                "Which is the next Test Case to execute? ",
                choices=[str(i) for i in test_cases_ids]
            )

            test_case_id = int(test_case_id)
            tests_cases_ids_ordered_by_user.append(test_case_id)
            test_cases_ids.remove(test_case_id)
            test_cases_ids = sorted(test_cases_ids)

        # Present Test Cases Execution Order to the User
        order_info = Text("\nThe Test Cases will be performed according " +
                          "to the following order: ", style="bold")
        order_info.append(str(tests_cases_ids_ordered_by_user), style="red")
        console.print(order_info)

        self.tests_cases_ids_ordered_by_user = tests_cases_ids_ordered_by_user
        return tests_cases_ids_ordered_by_user

    def _edit_test_cases_delete(self):
        test_id = Prompt.ask(
            "Which Test Case do you want to delete ('back' to go " +
            "back to the previous menu)?",
            choices=[str(tc.test_case_id) for tc in self.test_cases] +
            ["back"],
        )

        if test_id == "back":
            return

        delete = Confirm.ask("Are you sure you want to delete the " +
                             f"Test Case with the ID {test_id}?"
                             )

        # Delete the Test Case
        if delete:
            for tc in self.test_cases:
                if str(tc.test_case_id) == test_id:
                    del self.test_cases[self.test_cases.index(tc)]
                    break

    def _edit_test_cases_edit(self):
        console = Console()

        test_id = Prompt.ask(
            "Which Test Case do you want to edit ('back' to go " +
            "back to the previous menu)?",
            choices=[str(tc.test_case_id) for tc in self.test_cases] +
            ["back"],
        )

        if test_id == "back":
            return

        # gather the test case
        test_case = None
        for tc in self.test_cases:
            if str(tc.test_case_id) == test_id:
                test_case = tc
                break

        console.print(Text("\nTest Case Information:", style="bold"))

        panels = PrintAsPanelColumns(panels=[test_case.test.to_panel()])
        panels.print()

        console.print(Text("\nCurrent Test Case Definition:", style="bold"))

        panels = PrintAsPanelColumns(
            panels=[test_case.to_panel()]
        )
        panels.print()

        for variable, value in test_case.test_variables.items():
            info = Text()
            info.append("\nTest Variable: ", style="bold")
            info.append(variable + "\n")
            info.append("Current Value: ", style="bold")
            info.append(str(value) + "\n")
            console.print(info)

            edit = Confirm.ask("Do you want to edit this variable " +
                               f"({variable})?")
            if edit:
                # print Test Information
                new_value = Prompt.ask("New Value")
                test_case.add_test_variable(variable, new_value)

    def _edit_test_cases(self):
        # Print Header
        self._show_test_cases()
        show_test_cases = False

        op = ""
        while op != 'back':
            op = Prompt.ask(
                    "Do you want to edit or delete a Test Case ('back' "
                    "to go back to the main menu)? ",
                    choices=["edit", "delete", "back"],
                )

            if op == "back":
                break
            elif op == "delete":
                if show_test_cases:
                    self._show_test_cases()
                self._edit_test_cases_delete()
            elif op == "edit":
                self._edit_test_cases_edit()

            show_test_cases = True

    def _test_cases_prompt(self):
        panels = PrintAsTable(
            header=["ID", "Test Name", "Test Description"],
            rows=[
                [str(i+1), self.tests[i].name, self.tests[i].description]
                for i
                in range(len(self.tests))
            ]
        )
        prompts.display_tests_for_testbed(self.testbed_id)
        panels.print()

    def _confirm_testing_descriptor_output_file(self):
        console = Console()
        location_ok = False

        while not location_ok:
            info = Text()
            info.append("\nThe Testing Descriptor will be saved in the " +
                        "folllowing file: ", style="bold")
            info.append(self.output_filepath + "\n")
            console.print(info)
            change_filepath = Confirm.ask(
                "Do you wish to save the Testing Descriptor in a different " +
                "file?")

            if not change_filepath:
                location_ok = True
            else:
                file_path = Prompt.ask(
                    "Provide the file path where the Testing Descriptor " +
                    "should be saved ('back' to go back to the main menu)?")

                if file_path == "back":
                    continue

                elif os.path.isfile(file_path):
                    location_ok = True
                    self.output_filepath = file_path

                elif os.path.isdir(file_path):
                    self.output_filepath = os.path.join(
                        file_path,
                        "testing-descriptor.yaml"
                    )
                    location_ok = True
                else:
                    print(file_path)
                    print(os.path.isdir(file_path))
                    print(os.path.isfile(file_path))
                    info = Text("Impossible to save the Testing Descriptor " +
                                "in the specified location " +
                                f"{self.output_filepath}!",
                                style="red")
                    console.print(info)

            info = Text()
            info.append("\nThe Testing Descriptor will be saved in the " +
                        "folllowing file: ", style="bold")
            info.append(self.output_filepath + "\n")
            console.print(info)
        return True

    def _save_testing_decritptor(self):
        testing_descriptor = BASE_TESTING_DESCRIPTOR
        testing_descriptor["test_info"]["netapp_id"] = self.netapp_name
        testing_descriptor["test_info"]["network_service_id"] = self.ns_name
        testing_descriptor["test_info"]["testbed_id"] = self.testbed_id
        testing_descriptor["test_info"]["description"] = "Testing "\
            f"Descriptor for the {self.netapp_name} Network Application"

        testcases = []
        for tc in self.test_cases:
            tc_dict = {
                "testcase_id": tc.test_case_id,
                "type": tc.test.test_type,
                "name": tc.test.id,
                "description": tc.description,
                "parameters": []
            }
            for key, value in tc.test_variables.items():
                tc_dict["parameters"].append(
                    {
                        "key": key,
                        "value": value
                    }
                )

            testcases.append(tc_dict)

        testing_descriptor["test_phases"]["setup"]["testcases"] = testcases
        testing_descriptor["test_phases"]["execution"][0]["executions"]\
            [0]["testcase_ids"] = self.tests_cases_ids_ordered_by_user

        with open(self.output_filepath, 'w') as output_file:
            yaml.dump(
                testing_descriptor,
                output_file,
                default_flow_style=False,
                sort_keys=False
            )

        console = Console()
        console.print(Text("Generated Testing Descriptor:", style="bold"))

        print(
            yaml.dump(
                testing_descriptor,
                default_flow_style=False,
                sort_keys=False
            )
        )

        info = Text()
        info.append("\nThe Testing Descriptor was saved in the " +
                    "folllowing file: ", style="bold")
        info.append(self.output_filepath)
        console.print(info)

    def _test_cases_menu(self):

        while True:
            # Show testcases
            self._test_cases_prompt()

            # Present the Menu to the developer
            op = prompts.test_cases_operation()

            if op == "add":
                self._add_test()
            if op == "show":
                self._show_test_cases()
            if op == "info":
                self._show_test_info()
            if op == "edit":
                self._edit_test_cases()
            if op == "finish":
                self._finish_test_cases_definition()
                if self._confirm_testing_descriptor_output_file():
                    break

    def create_testing_descriptor(self):
        self._test_cases_menu()
        self._save_testing_decritptor()
