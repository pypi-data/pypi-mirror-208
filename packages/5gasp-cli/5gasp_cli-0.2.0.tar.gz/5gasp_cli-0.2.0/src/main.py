# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-02-01 16:31:36
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-05-15 17:40:46

from typing import List, Optional
from .helpers.beatiful_prints import PrintAsTable, PrintAsPanelColumns
from rich.prompt import Prompt, Confirm
import typer

from .CICDManagerAPIClient import apli_client as CICD_API_Client
from .DescriptorParser.parser import ConnectionPointsParser
from .TestingDescriptorGenerator.descriptor_generator import \
    TestingDescriptorGenerator
from .helpers import constants as Constants
from .helpers import prompts

app = typer.Typer()
state = {"verbose": False}


def _list_testbeds(api_client, print_info=False, centered=False):
    testbeds = api_client.get_all_testbeds()
    # Print table with the available testbeds
    if print_info:
        table = PrintAsTable(
            header=["ID", "Name", "Description"],
            rows=[
                [t["id"], t["name"], t["description"]]
                for t
                in testbeds
            ]
        )
        table.print(centered=centered)
    return testbeds


def _list_tests(api_client, testbed_id, print_info=False):
    tests = api_client.get_tests_per_testbed(testbed_id)
    if print_info:
        panels = PrintAsPanelColumns(
            panels=[t.to_panel() for t in tests]
        )
        panels.print()
    return tests


@app.command()
def create_testing_descriptor(
    output_filepath: str = typer.Option(
        default="testing-descriptor.yaml",
        help="Output filepath"
    ),
    infer_tags_from_nsd: Optional[List[str]] = typer.Option(
        default=None
    )
):
    # 1. Check if the developer wants to infer tags from an NSD
    if infer_tags_from_nsd:
        
        # Information Prompt
        prompts.connection_points_information_prompt()

        # Parse connection points information
        tags_parser = ConnectionPointsParser(infer_tags_from_nsd)
        existing_connect_points = tags_parser.connection_points

        print("\nThe following NSDs can be used for inferring connection " +
              "points:"
              )

        table = PrintAsTable(
            header=["NSD's File Path", "NSD ID", "Inferred Connection Points"],
            rows=[
                [
                    nsd_file_path,
                    nsd_info["ns_id"],
                    "\n".join(nsd_info["connection_points"])
                ]
                for nsd_file_path, nsd_info
                in existing_connect_points.items()
            ]
        )
        table.print()

        prompts.connection_point_keys(
            list(existing_connect_points.values())[0]["connection_points"][0]
        )

        # 2. Ask the developer if he wishes to proceed
        proceed = Confirm.ask(
            "\nDo you wish to proceed with the Test Descriptor's creation?"
            )

        # Exit if the developer does not want to proceed
        if not proceed:
            return

    # 3. Ask for the Testing Descriptor initial information
    netapp_name = input("\n" + Constants.USER_PROMPTS.NETAPP_NAME.value)
    ns_name = input(Constants.USER_PROMPTS.NS_NAME.value)

    api_client = CICD_API_Client.CICDManagerAPIClient()

    # Print table with the available testbeds
    # List Testbeds
    testbeds = _list_testbeds(
        api_client=api_client,
        print_info=True,
        centered=True
    )
    # Prompt to choose a testbed
    testbed_id = Prompt.ask(
        "\nIn which testbed do you want to validate your Network " +
        "Application?",
        choices=[t["id"] for t in testbeds]
    )

    tests = _list_tests(
        api_client=api_client,
        testbed_id=testbed_id,
        print_info=False
    )

    generator = TestingDescriptorGenerator(
        connection_points=existing_connect_points if infer_tags_from_nsd else None,
        netapp_name=netapp_name,
        ns_name=ns_name,
        testbed_id=testbed_id,
        tests=tests,
        output_filepath=output_filepath
    )

    generator.create_testing_descriptor()


@app.command()
def list_testbeds():
    '''
    List available testbeds
    '''
    api_client = CICD_API_Client.CICDManagerAPIClient()

    # List Testbeds
    testbeds = _list_testbeds(
        api_client=api_client,
        print_info=True
    )

    # Ask the user if he wishes to list the available test cases in each of
    # the available testbeds
    should_list_tests = Confirm.ask(
        "\nDo you wish to list the available tests for one of these testbeds?",
    )

    # If the answer is 'yes'
    if should_list_tests:
        testbed_id = Prompt.ask(
            "\nFor which testbed do you wish to list the available tests",
            choices=[t["id"] for t in testbeds]
        )

        print(f"\nAvailable tests in testbed '{testbed_id}':\n")

        _list_tests(
            api_client=api_client,
            testbed_id=testbed_id,
            print_info=True
        )


@app.command()
def list_available_tests():
    '''
    List available tests to developer
    '''

    prompts.tests_per_testbed_prompt()

    # Print all the available testbeds
    prompts.tests_testbeds_list_prompt()

    ApiClient = CICD_API_Client.CICDManagerAPIClient()
    # List Testbeds
    testbeds = _list_testbeds(
        api_client=ApiClient,
        print_info=True,
        centered=True
    )

    # Prompt to choose a testbed
    testbed_id = Prompt.ask(
        "\nFor which testbed do you wish to list the available tests",
        choices=[t["id"] for t in testbeds]
    )

    # List testbed's available tests
    tests = _list_tests(
        api_client=ApiClient,
        testbed_id=testbed_id,
        print_info=False
    )

    while True:
        panels = PrintAsTable(
            header=["ID", "Test Name", "Test Description"],
            rows=[
                [str(i+1), tests[i].name, tests[i].description]
                for i
                in range(len(tests))
            ]
        )
        prompts.display_tests_for_testbed(testbed_id)
        panels.print()

        # Does the user wishes to see additional tests information?

        prompts.do_you_wish_to_see_test_information_prompt()

        test_details = Prompt.ask(
                "For which test do you wish to see additional information? ",
                choices=[str(i) for i in range(1, len(tests)+1)] + ["exit"]
            )

        if test_details == "exit":
            break

        panels = PrintAsPanelColumns(
                panels=[tests[int(test_details)-1].to_panel(expand=True)]
            )
        panels.print()


@app.callback()
def main(
    verbose: bool = False,
    ci_cd_manager_url: str = typer.Option(
        default=Constants.CI_CD_SERVICE_URL,
        help="CI/CD Manager URL to override the default one."
    )
):
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True
    # Set the ci_cd_manager_url
    Constants.CI_CD_SERVICE_URL = ci_cd_manager_url


if __name__ == "__main__":

    app()
