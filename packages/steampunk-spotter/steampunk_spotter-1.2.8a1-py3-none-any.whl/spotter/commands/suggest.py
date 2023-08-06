"""Provide suggest CLI command."""

import argparse
import json
import os
import sys
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional

from spotter.api import ApiClient
from spotter.storage import Storage


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for suggest command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "suggest", argument_default=argparse.SUPPRESS, description="Get suggestions from Spotter's AI component"
    )
    parser.add_argument(
        "--num-results", "-n", type=int, default=5, choices=range(1, 51), metavar="[1, 50]",
        help="Number of expected suggestions"
    )
    parser.add_argument(
        "query", type=str, help="Query that will be used to produce a suggestion from Spotter's AI component"
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace) -> None:
    """
    Execute callback for suggest command.

    :param args: Argparse arguments
    """
    api_endpoint = args.endpoint or os.environ.get("SPOTTER_ENDPOINT", None)
    storage_path = args.storage_path or Storage.DEFAULT_PATH
    api_token = args.api_token or os.environ.get("SPOTTER_API_TOKEN")
    username = args.username or os.environ.get("SPOTTER_USERNAME")
    password = args.password or os.environ.get("SPOTTER_PASSWORD")

    suggestions = suggest(api_endpoint, storage_path, api_token, username, password, args.query, args.num_results)

    try:
        print(json.dumps(suggestions, indent=2))
    except TypeError as e:
        print(f"Error: unable to serialize the object to JSON: {str(e)}", file=sys.stderr)
        sys.exit(2)


# pylint: disable=too-many-locals
def suggest(api_endpoint: Optional[str], storage_path: Path, api_token: Optional[str], username: Optional[str],
            password: Optional[str], query: str, num_results: int) -> List[Dict[str, Any]]:
    """
    Suggest module and task examples by calling Spotter's AI component.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param query: Query that will be used to produce a suggestion from Spotter's AI component
    :param num_results: Number of expected suggestions
    :return: List of suggestions
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

    api_client = ApiClient(endpoint, storage, api_token, username, password)
    query_params = urllib.parse.urlencode({"query": query, "num_results": num_results})
    response = api_client.get(f"/v2/ai/query/modules/?{query_params}")

    try:
        response_json = response.json()
        results: List[Dict[str, Any]] = response_json.get("results", [])
        results.sort(key=lambda k: k.get("score", 0), reverse=True)
        return results
    except json.JSONDecodeError as e:
        print(f"Error: scan result cannot be converted to JSON: {str(e)}", file=sys.stderr)
        sys.exit(2)
