# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-04-04 16:39:57
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-05-15 22:51:18

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.console import Group

from ..helpers.connection_point_tags import CONNECTION_POINT_TAGS
from ..helpers.beatiful_prints import PrintAsTable
from rich.prompt import Prompt


def test_cases_operation():
    prompt = Text()

    console = Console()
    prompt.append("\nWhich Operation do you want to perform?\n")

    prompt.append("(add)  ", style="bold")
    prompt.append("Add new Test Case\n")

    prompt.append("(info) ", style="bold")
    prompt.append("Get more information regarding a Test\n")

    prompt.append("(show) ", style="bold")
    prompt.append("Show already configured Test Cases\n")

    prompt.append("(edit) ", style="bold")
    prompt.append("Edit Test Cases\n")

    prompt.append("(finish) ", style="bold")
    prompt.append("Finish the Test Cases Configuration\n")

    console.print(prompt)

    operation = Prompt.ask(
        "Which Operation do you want to perform? ",
        choices=["add", "info", "show", "edit", "finish"]
    )
    return operation


def tests_per_testbed_prompt():
    console = Console()
    group = Group(
        Align.center("[b]In 5GASP, each testbed has its own specific " +
                     "tests.[/b]"),
        Align.center(" "),
        Align.center("Thus, we don't provide and overall view of the tests " +
                     "we have in our ecosystem, but rather a testbed-level " +
                     "view of the tests."),
        Align.center("[b]This way, you must first choose a testbed on where " +
                     "yourNetApp shall be deployed, valdiated and " +
                     "certified.[/b]"),
        Align.center("Only after choosing the testbed you may list the " +
                     "tests available in that facility."),
    )
    console.print(
        Align.center(
            Panel(
                renderable=group,
                title="5GASP's Tests",
                expand=True
            )
        )
    )


def tests_testbeds_list_prompt():
    console = Console()
    console.print(
        Align.center(
            "\n[b]Testbeds Available for Network Applications Testing:[/b]\n"
        )
    )


def display_tests_for_testbed(testbed):
    console = Console()
    console.print(
        "\n[b]" +
        f"The Testbed '{testbed}' provides the following tests:".title() +
        "[/b]\n"
    )


def do_you_wish_to_see_test_information_prompt():
    console = Console()
    console.print(
        "\n[b]You can see additional information about each of the tests.\n" +
        "If you don't want to do so, just type 'exit'.[b]"
    )


def connection_points_information_prompt():
    console = Console()
    group = Group(
        Align.center("[b]5GASP's CLI only supports inferring " +
                     "connection points when they refer to a VNF.[/b]"),
        Align.center(" "),
        Align.center("We currently do not support CNF-related connection " +
                     "points."),
        Align.center("If you want to create a Testing Descriptor for a " +
                     "CNF-based  Network Application, please contact us at " +
                     "[b]contact@5gasp.eu[/b], and we will support your " +
                     "though the development of your Testing Descriptor."
                     ),
        )
    console.print(
        Align.center(
            Panel(
                renderable=group,
                title="Connection Points",
                expand=True
            )
        )
    )


def connection_point_keys(example_connection_point):
    console = Console()
    group = Group(
        Align.center("[b]From the previously presented Connection Points it " +
                     "is possible to define several template tags that " +
                     "shall be rendered after the deployment of the Network " +
                     "Application.[/b]"),

        Align.center(" "),
        Align.center("For instance, if a developer wishes to perform a " +
                     "test that requires information on the IPs of the " +
                     "Network Application VNFs, the devoloper may define a " +
                     "template tag, which will be rendered to the IP of a " +
                     "certain VNF " +
                     "({{<ns_id>|<vnf_id>|<connection_point>|ip-address}})."),
        Align.center(" "),
        )

    print()
    console.print(
        Align.center(
            Panel(
                renderable=group,
                title="Connection Points - Template Tags",
                expand=True
            )
        )
    )
    print("\nThe available template tags are the following:")

    tmp_example_connection_point = example_connection_point[:-2]

    header = ["Connection Point Key", "Description", "Example",
              "Example Value"]
    rows = []
    for tag, info in CONNECTION_POINT_TAGS.items():
        rows.append(
            [
                tag,
                info["description"],
                tmp_example_connection_point + "|" + tag + "}}",
                str(info["example"])
            ]
        )

    print_as_table = PrintAsTable(header=header, rows=rows)
    print_as_table.print()
