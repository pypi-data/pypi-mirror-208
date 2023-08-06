# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-04-20 13:03:58
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-04-26 23:24:28

from rich.panel import Panel


class Test:
    def __init__(self, id=None, name=None, description=None,  mandatory=None,
                 test_variables=None):
        self.id = id
        self.name = name
        self.description = description
        self.mandatory = mandatory
        self.test_variables = test_variables
        self.test_type = None

    def load_from_dict(self, test_dict):
        self.id = test_dict["id"]
        self.name = test_dict["name"]
        self.description = test_dict["description"]
        self.mandatory = test_dict["mandatory"]
        self.test_type = "predefined"

        self.test_variables = []
        if "test_variables" in test_dict:
            for test_variable in test_dict["test_variables"]:
                self.test_variables.append(
                    TestVariable(
                        name=test_variable["variable_name"],
                        description=test_variable["description"],
                        mandatory=test_variable["mandatory"],
                        possible_options=test_variable["possible_options"],
                        type=test_variable["type"],
                        can_be_injected_by_the_nods=test_variable[
                            "can_be_injected_by_the_nods"
                        ]
                    )
                )

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "mandatory": self.mandatory,
            "test_variable": self.test_variables
        }

    def __str__(self):
        return str(self.__dict__())

    def to_panel(self, expand=None, width=None):
        panel_str = f"""
        [b]{self.name.title()} Test[/b]

        [yellow]Test ID:[/yellow] {self.id}
        [yellow]Test Description:[/yellow] {self.description}

        [blue][b]Test Variables: [/b]
        """

        if len(self.test_variables) == 0:
            panel_str += """
            [blue]This test requires no parameters[/blue]
            """

        for tv in self.test_variables:
            panel_str += f"""
            [blue]◉ {tv.name}:
            \t[blue]○ Description:[/blue][white] {tv.description}
            \t[blue]○ Mandatory:[/blue]  {tv.mandatory}
            \t[blue]○ Type:[/blue]  {tv.type}
            """

            if len(tv.possible_options) != 0:
                panel_str += "\t[blue]○ Possible Options:[/blue] "
                panel_str += str(tv.possible_options) + "\n"

        if expand:
            print("dddd")
            return Panel(renderable=panel_str, expand=True)
        if width:
            return Panel(renderable=panel_str, expand=False, width=width)
        if not expand and not width:
            return Panel(renderable=panel_str, expand=False, width=65)


class TestVariable:
    def __init__(self, name, description, mandatory, possible_options, type,
                 can_be_injected_by_the_nods):
        self.name = name
        self.description = description
        self.mandatory = mandatory
        self.possible_options = possible_options
        self.type = type
        self.can_be_injected_by_the_nods = can_be_injected_by_the_nods

    def to_panel(self, test_name, expand=None, width=None):

        possible_values = self.possible_options \
            if len(self.possible_options) != 0 \
            else "Not Applicable"

        injected = "Yes" if self.can_be_injected_by_the_nods else "No"

        panel_str = f"""
[blue]Test Name:[/blue] {test_name}
[b]Test Variable:[/b] {self.name}

[yellow]Test Variable Name:[/yellow] {self.name}
[yellow]Test Variable Description:[/yellow] {self.description}
[yellow]Test Variable Possible Values:[/yellow] {possible_values}
[yellow]Test Variable Type:[/yellow] {self.type}
[yellow]Can Test Variable Be Injected By The NODS:[/yellow] {injected}
        """
        if expand:
            return Panel(renderable=panel_str, expand=True)
        if width:
            return Panel(renderable=panel_str, expand=False, width=width)
        if not expand and not width:
            return Panel(renderable=panel_str, expand=False, width=65)


class TestCase:
    def __init__(self, test, description=None, test_case_id=None):
        self.test = test
        self.test_variables = {}
        self.description = description
        self.test_case_id = test_case_id

    def add_test_variable(self, key, value):
        self.test_variables[key] = value

    def to_panel(self, show_configured=False, expand=None, width=None):
        panel_str = ""

        # Show message stating that the test case was fully configured
        if show_configured:
            panel_str += f"""
[b]Test '{self.test.name}' has been configured![/b]
"""
        # Fill in the rest of the panel with other test info
        panel_str += f"""
[blue]Test Name:[/blue] {self.test.name}
[blue]Test Case ID:[/blue] {self.test_case_id}
        """
        for variable, value in self.test_variables.items():
            panel_str += f"""
[yellow]{variable}:[/yellow] {value}"""
        if expand:
            return Panel(renderable=panel_str, expand=True)
        if expand is False:
            return Panel(renderable=panel_str, expand=False)
        if width:
            return Panel(renderable=panel_str, expand=False, width=width)
        if not expand and not width:
            return Panel(renderable=panel_str, expand=False, width=65)
