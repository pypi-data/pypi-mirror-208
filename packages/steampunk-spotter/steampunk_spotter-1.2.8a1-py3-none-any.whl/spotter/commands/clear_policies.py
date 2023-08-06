"""Provide clear-policies CLI command."""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from spotter.api import ApiClient
from spotter.storage import Storage


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for clear-policies command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "clear-policies", help="Clear custom policies (enterprise feature)",
        description="Clear OPA policies for custom Spotter checks (enterprise feature)"
    )
    project_organization_group = parser.add_mutually_exclusive_group()
    project_organization_group.add_argument(
        "--project-id", "-p", type=str,
        help="UUID of an existing Steampunk Spotter project to clear custom policies from "
             "(default project from the personal organization will be used if not specified)"
    )
    project_organization_group.add_argument(
        "--organization-id", type=str, help="UUID of an existing Steampunk Spotter organization to clear custom "
                                            "policies from"
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace) -> None:
    """
    Execute callback for clear-policies command.

    :param args: Argparse arguments
    """
    api_endpoint = args.endpoint or os.environ.get("SPOTTER_ENDPOINT", None)
    storage_path = args.storage_path or Storage.DEFAULT_PATH
    api_token = args.api_token or os.environ.get("SPOTTER_API_TOKEN")
    username = args.username or os.environ.get("SPOTTER_USERNAME")
    password = args.password or os.environ.get("SPOTTER_PASSWORD")

    clear_policies(api_endpoint, storage_path, api_token, username, password, args.project_id, args.organization_id)


# pylint: disable=too-many-arguments,too-many-locals
def clear_policies(api_endpoint: Optional[str], storage_path: Path, api_token: Optional[str], username: Optional[str],
                   password: Optional[str], project_id: Optional[str], organization_id: Optional[str]) -> None:
    """
    Clear custom OPA policies.

    By default, this will clear policies that belong to the default project from personal organization.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param project_id: UUID of an existing Steampunk Spotter project to clear custom policies from
    :param organization_id: UUID of an existing Steampunk Spotter organization to clear custom policies from
    """
    storage = Storage(storage_path)

    # TODO: extract this to a separate configuration component along with other configuration file options
    if api_endpoint is None:
        if storage.exists("spotter.json"):
            storage_configuration_json = storage.read_json("spotter.json")
            endpoint = storage_configuration_json.get("endpoint", ApiClient.DEFAULT_ENDPOINT)
        else:
            endpoint = ApiClient.DEFAULT_ENDPOINT
    else:
        endpoint = api_endpoint

    payload: Dict[str, Any] = {
        "policies": [],
        "project_id": project_id,
        "organization_id": organization_id
    }

    api_client = ApiClient(endpoint, storage, api_token, username, password)
    response = api_client.put("/v2/opa/", payload=payload, ignore_response_status_codes=True)
    if response.status_code == 403:
        print("The use of custom policies is only available in Spotter's ENTERPRISE plan. "
              "Please upgrade your plan to use this functionality.")
        sys.exit(0)
    if not response.ok:
        print(api_client.format_api_error(response), file=sys.stderr)
        sys.exit(2)

    print("Custom policies successfully cleared.")
