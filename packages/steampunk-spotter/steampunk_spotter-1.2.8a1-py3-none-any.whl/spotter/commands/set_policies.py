"""Provide set-policies CLI command."""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from spotter.api import ApiClient
from spotter.storage import Storage


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for set-policies command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "set-policies", help="Set custom policies (enterprise feature)",
        description="Set OPA policies (written in Rego Language) for custom Spotter checks (enterprise feature)"
    )
    project_organization_group = parser.add_mutually_exclusive_group()
    project_organization_group.add_argument(
        "--project-id", "-p", type=str,
        help="UUID of an existing Steampunk Spotter project to set custom policies for "
             "(default project from the personal organization will be used if not specified)"
    )
    project_organization_group.add_argument(
        "--organization-id", type=str, help="UUID of an existing Steampunk Spotter organization to set custom "
                                            "policies for"
    )
    parser.add_argument(
        "path", type=lambda p: Path(p).absolute(),
        help="Path to the file or folder with custom OPA policies (written in Rego Language)"
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace) -> None:
    """
    Execute callback for include-policies command.

    :param args: Argparse arguments
    """
    api_endpoint = args.endpoint or os.environ.get("SPOTTER_ENDPOINT", None)
    storage_path = args.storage_path or Storage.DEFAULT_PATH
    api_token = args.api_token or os.environ.get("SPOTTER_API_TOKEN")
    username = args.username or os.environ.get("SPOTTER_USERNAME")
    password = args.password or os.environ.get("SPOTTER_PASSWORD")

    path: Path = args.path
    if not path.exists():
        print(f"Error: Path at {path} provided for scanning does not exist.", file=sys.stderr)
        sys.exit(2)
    if not path.is_file() and not path.is_dir():
        print(f"Error: Path at {path} is not a file or directory.", file=sys.stderr)
        sys.exit(2)

    include_policies(
        api_endpoint, storage_path, api_token, username, password, args.project_id, args.organization_id, path
    )


# pylint: disable=too-many-arguments,too-many-locals
def include_policies(api_endpoint: Optional[str], storage_path: Path, api_token: Optional[str], username: Optional[str],
                     password: Optional[str], project_id: Optional[str], organization_id: Optional[str],
                     path: Path) -> None:
    """
    Set custom OPA policies.

    By default, this will set policies for the default project from personal organization.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param project_id: UUID of an existing Steampunk Spotter project to set custom policies for
    :param organization_id: UUID of an existing Steampunk Spotter organization to set custom policies for
    :param path: Path to the file or folder with custom OPA policies (written in Rego Language)
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

    policies: List[Dict[str, Any]] = []
    if path.is_file():
        item = {
            "policy_name": path.name,
            "policy_rego": path.read_text(),
            "severity": "",
            "description": "",
            "type": "CUSTOM"
        }
        policies.append(item)
    else:
        for task_file in path.rglob("*.rego"):
            item = {
                "policy_name": task_file.name,
                "policy_rego": task_file.read_text(),
                "severity": "",
                "description": "",
                "type": "CUSTOM"
            }
            policies.append(item)

    payload = {
        "policies": policies,
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

    print("Custom policies successfully set.")
