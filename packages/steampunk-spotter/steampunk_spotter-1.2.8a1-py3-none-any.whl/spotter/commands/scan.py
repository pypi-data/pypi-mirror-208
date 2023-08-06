"""Provide scan CLI command."""

import argparse
import json
import os
import re
import sys
import time
import xml
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, cast

import pydantic.dataclasses
import yaml
from colorama import Fore, Style
from pydantic.json import pydantic_encoder

from spotter.api import ApiClient
from spotter.environment import Environment
from spotter.parsing import parse_ansible_artifacts, ParsingResult

from spotter.reporting.report import JUnitXml
from spotter.rewriting.processor import update_files
from spotter.rewriting.models import RewriteSuggestion, CheckType
from spotter.storage import Storage
from spotter.utils import prompt_yes_no_question


class DisplayLevel(Enum):
    """Enum that holds different levels/statuses for check result."""

    SUCCESS = 0
    HINT = 1
    WARNING = 2
    ERROR = 3

    def __str__(self) -> str:
        """
        Convert DisplayLevel to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, level: str) -> "DisplayLevel":
        """
        Convert string level to DisplayLevel object.

        :param level: Check result level
        :return: DisplayLevel object
        """
        try:
            return cls[level.upper()]
        except KeyError:
            print(f"Error: nonexistent check status display level: {level}, "
                  f"valid values are: {list(str(e) for e in DisplayLevel)}.")
            sys.exit(2)


class Profile(Enum):
    """Enum that holds profiles with different checks for scanning."""

    DEFAULT = 0
    FULL = 1
    SECURITY = 2

    def __str__(self) -> str:
        """
        Convert Profile to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, profile: str) -> "Profile":
        """
        Convert string profile to Profile object.

        :param profile: Profile for scanning
        :return: Profile object
        """
        try:
            return cls[profile.upper()]
        except KeyError:
            print(f"Error: nonexistent profile: {profile}, "
                  f"valid values are: {list(str(e) for e in Profile)}.")
            sys.exit(2)


class OutputFormat(Enum):
    """Enum that holds different output formats for scan result."""

    TEXT = 1
    JSON = 2
    YAML = 3
    JUNIT_XML = 4

    def __str__(self) -> str:
        """
        Convert OutputFormat to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, output_format: str) -> "OutputFormat":
        """
        Convert string level to OutputFormat object.

        :param output_format: Scan result output format
        :return: OutputFormat object
        """
        try:
            return cls[output_format.upper()]
        except KeyError:
            print(f"Error: nonexistent output format: {output_format}, "
                  f"valid values are: {list(str(e) for e in OutputFormat)}.")
            sys.exit(2)


@pydantic.dataclasses.dataclass
class ItemMetadata:
    """A container for item metadata originating from the original task or play."""

    file_name: str
    line: int
    column: int

    @classmethod
    def from_item_meta(cls, item_meta: Dict[str, Any]) -> "ItemMetadata":
        """
        Convert task metadata to ItemMetadata object for storing metadata for Ansible task or play.

        :param task_meta: Ansible task spotter_metadata content.
        :return: TaskMetadata object
        """
        file_name = item_meta.get("file", "")
        line = item_meta.get("line", "")
        column = item_meta.get("column", "")

        try:
            # trim the part of the directory that is shared with CWD if this is possible
            file_name = str(Path(file_name).relative_to(Path.cwd()))
        except ValueError:
            pass

        return cls(
            file_name=file_name,
            line=line,
            column=column
        )


@pydantic.dataclasses.dataclass
class ScanPayload:
    """A container for information about the scan payload/input."""

    environment: Environment
    tasks: List[Dict[str, Any]]
    playbooks: List[Dict[str, Any]]

    @classmethod
    def from_json_file(cls, import_path: Path) -> "ScanPayload":
        """
        Load ScanPayload object from JSON file.

        :param import_path: File path with JSON to import from
        :return: ScanPayload object holding input tuple (environment, tasks, playbooks)
        """
        try:
            if not import_path.exists():
                print(f"Error: import file at {import_path} does not exist.")
                sys.exit(2)

            with import_path.open("r", encoding="utf-8") as import_file:
                scan_payload = json.load(import_file)
                environment_dict = scan_payload.get("environment", None)
                if environment_dict is not None:
                    environment = Environment(**environment_dict)
                else:
                    environment = Environment()

                return cls(
                    environment=environment,
                    tasks=scan_payload.get("tasks", []),
                    playbooks=scan_payload.get("playbooks", [])
                )
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error: {str(e)}")
            sys.exit(2)

    @classmethod
    def from_args(cls, parsing_result: ParsingResult, environment: Environment, include_metadata: bool,
                  import_payload: Optional[Path]) -> "ScanPayload":
        """
        Convert CLI arguments to ScanPayload object.

        :param parsing_result: ParsingResult object
        :param environment: Environment object
        :param include_metadata: Upload metadata (i.e., file names, line and column numbers)
        :param import_payload: Path to file where ScanPayload can be imported from
        :return: ScanPayload object
        """
        if import_payload:
            return cls.from_json_file(import_payload)

        return cls(
            environment=environment,
            tasks=parsing_result.tasks if include_metadata else parsing_result.tasks_without_metadata(),
            playbooks=parsing_result.playbooks if include_metadata else parsing_result.playbooks_without_metadata()
        )

    def to_json_file(self, export_path: Path) -> None:
        """
        Export scan payload to JSON file.

        :param export_path: File path to export to (will be overwritten if exists)
        """
        try:
            with export_path.open("w", encoding="utf-8") as export_file:
                json.dump(pydantic_encoder(self), export_file, indent=2)
        except TypeError as e:
            print(f"Error: {str(e)}")
            sys.exit(2)


@pydantic.dataclasses.dataclass
class CheckCatalogInfo:
    """A container for information about the specific check in check catalog from the backend."""

    event_code: str
    event_value: str
    event_message: str
    check_class: str

    @classmethod
    def from_api_response_element(cls, element: Dict[str, Any]) -> "CheckCatalogInfo":
        """
        Convert element entry from scan API response to CheckCatalogInfo object.

        :param element: An 'element' JSON entry from scan API response
        :return: CheckCatalogInfo object
        """
        return cls(
            event_code=element.get("event_code", ""),
            event_value=element.get("event_value", ""),
            event_message=element.get("event_message", ""),
            check_class=element.get("check_class", "")
        )


@pydantic.dataclasses.dataclass
class CheckResult:
    """A container for parsed check results originating from the backend."""

    correlation_id: str
    original_item: Dict[str, Any]
    metadata: Optional[ItemMetadata]
    catalog_info: CheckCatalogInfo
    level: DisplayLevel
    message: str
    suggestion: Optional[RewriteSuggestion]
    doc_url: Optional[str]
    check_type: CheckType

    def construct_output(self, disable_colors: bool = False, disable_docs_url: bool = False) -> str:
        """
        Construct CheckResult output using its properties.

        :param disable_colors: Disable output colors and styling
        :param disable_docs_url: Disable outputting URL to documentation
        :return: Formatted output for check result
        """
        # or: we can have results that relate to Environment - no file and position
        metadata = self.metadata or ItemMetadata(file_name="", line=0, column=0)
        result_level = self.level.name.strip().upper()
        file_location = f"{metadata.file_name}:{metadata.line}:{metadata.column}"
        out_prefix = f"{file_location}: {result_level}: [{self.catalog_info.event_code}]"
        out_message = self.message.strip()
        if not disable_colors:
            if result_level == DisplayLevel.ERROR.name:
                out_prefix = Fore.RED + out_prefix + Fore.RESET
                out_message = re.sub(r"'([^']*)'", Style.BRIGHT + Fore.RED + r"\1" + Fore.RESET + Style.NORMAL,
                                     out_message)
            elif result_level == DisplayLevel.WARNING.name:
                out_prefix = Fore.YELLOW + out_prefix + Fore.RESET
                out_message = re.sub(r"'([^']*)'", Style.BRIGHT + Fore.YELLOW + r"\1" + Fore.RESET + Style.NORMAL,
                                     out_message)
            else:
                out_message = re.sub(r"'([^']*)'", Style.BRIGHT + r"\1" + Style.NORMAL, out_message)

        output = f"{out_prefix} {out_message}".strip()
        if not output.endswith("."):
            output += "."
        if not disable_docs_url and self.doc_url:
            output = f"{output} View docs at {self.doc_url}."

        return output


@pydantic.dataclasses.dataclass
class ScanSummary:
    """A container for scan result summary."""

    scan_time: float
    num_errors: int
    num_warnings: int
    num_hints: int
    status: str

    def update(self, check_result: Optional[CheckResult]) -> None:
        """
        Update summary information.

        If check_result is not set the summary does not change, otherwise
        summary update respects CheckResult.level field.
        """
        if not check_result:
            return

        if check_result.level == DisplayLevel.ERROR:
            self.num_errors += 1
        elif check_result.level == DisplayLevel.WARNING:
            self.num_warnings += 1
        else:
            self.num_hints += 1


@pydantic.dataclasses.dataclass
class ScanResult:
    """A container for scan result originating from the backend."""

    # TODO: Add more fields from scan response if we need them
    uuid: Optional[str]
    user: Optional[str]
    user_info: Optional[Dict[str, Any]]
    project: Optional[str]
    environment: Optional[Dict[str, Any]]
    scan_date: Optional[str]
    subscription: Optional[str]
    is_paid: Optional[bool]
    summary: ScanSummary
    check_results: List[CheckResult]

    @classmethod
    def from_api_response(
            cls, response_json: Dict[str, Any],
            input_tasks: List[Dict[str, Any]],
            input_playbooks: List[Dict[str, Any]],
            scan_time: float
    ) -> "ScanResult":
        """
        Convert scan API response to ScanResult object.

        :param response_json: The backend API response in JSON format
        :param input_tasks: The scanned tasks with no information removed
        :param scan_time: Time taken to do a scan
        :return: ScanResult object
        """
        scan_result = cls(
            uuid=response_json.get("id", ""),
            user=response_json.get("user", ""),
            user_info=response_json.get("user_info", {}),
            project=response_json.get("project", ""),
            environment=response_json.get("environment", {}),
            scan_date=response_json.get("scan_date", ""),
            subscription=response_json.get("subscription", ""),
            is_paid=response_json.get("is_paid", False),
            summary=ScanSummary(
                scan_time=scan_time,
                num_errors=0,
                num_warnings=0,
                num_hints=0,
                status=response_json.get("status", "")),
            check_results=[]
        )
        scan_result.parse_check_results(response_json, input_tasks, input_playbooks)
        return scan_result

    def _parse_known_check_result(self, element: Dict[str, Any], input_items: Dict[str, Dict[str, Any]]
                                  ) -> Optional[CheckResult]:
        check_type: CheckType = CheckType.from_string(element.get("check_type", ""))
        if check_type not in [CheckType.TASK, CheckType.PLAY]:
            print(f"Incorrect check type '{check_type}'. Should be one of [{CheckType.TASK},{CheckType.PLAY}]")
            sys.exit(2)

        correlation_id = element.get("correlation_id")
        if not correlation_id:
            print("Correlation is for result was not set. Shouls not happen for task or play.")
            sys.exit(2)

        # guard against incomplete results where we don't match a task or play
        original_item = input_items.get(correlation_id)
        if not original_item:
            print("Could not map task ID to its original task.")
            return None

        # guard against missing task or play args and metadata
        item_meta = original_item.get("spotter_metadata", None)
        if not item_meta:
            print("Meta data is missing.")
            return None

        suggestion = element.get("suggestion", "")
        item_metadata_object = ItemMetadata.from_item_meta(item_meta)
        suggestion_object: Optional[RewriteSuggestion] = \
            RewriteSuggestion.from_item(check_type, original_item, suggestion)
        display_level = DisplayLevel.from_string(element.get("level", ""))

        result = CheckResult(
            correlation_id=correlation_id, original_item=original_item, metadata=item_metadata_object,
            catalog_info=CheckCatalogInfo.from_api_response_element(element), level=display_level,
            message=element.get("message", ""), suggestion=suggestion_object, doc_url=element.get("doc_url", ""),
            check_type=check_type
        )
        return result

    def _parse_unknown_check_result(self, element: Dict[str, Any]) -> CheckResult:
        check_type = CheckType.from_string(element.get("check_type", ""))
        display_level = DisplayLevel.from_string(element.get("level", ""))
        check_catalog_info = CheckCatalogInfo.from_api_response_element(element)

        result = CheckResult(
            correlation_id="", original_item={}, metadata=None, catalog_info=check_catalog_info, level=display_level,
            message=element.get("message", ""), suggestion=None, doc_url=element.get("doc_url", ""),
            check_type=check_type
        )
        return result

    def parse_check_results(
            self,
            response_json: Dict[str, Any],
            input_tasks: List[Dict[str, Any]],
            input_playbooks: List[Dict[str, Any]]) -> None:
        """
        Parse result objects and map tasks with complete information.

        :param response_json: The backend API response in JSON format
        :param input_tasks: The scanned tasks with no information removed
        """
        tasks_as_dict = {x["task_id"]: x for x in input_tasks if "task_id" in x}
        plays_as_dict = {}
        for playbook in input_playbooks:
            plays_as_dict.update({x["play_id"]: x for x in playbook["plays"] if "play_id" in x})

        result: List[CheckResult] = []
        for element in response_json.get("elements", []):
            check_type = CheckType.from_string(element.get("check_type", ""))
            item: Optional[CheckResult] = None

            if check_type == CheckType.TASK:
                item = self._parse_known_check_result(element, tasks_as_dict)
            elif check_type == CheckType.PLAY:
                item = self._parse_known_check_result(element, plays_as_dict)
            else:
                item = self._parse_unknown_check_result(element)

            if item:
                self.summary.update(item)
                result.append(item)
        self.check_results = result

    def filter_check_results(self, threshold: DisplayLevel) -> None:
        """
        Filter a list of check results by only keeping tasks over a specified severity level.

        :param threshold: The DisplayLevel object as threshold (inclusive) of what level messages (and above) to keep
        """
        self.check_results = [cr for cr in self.check_results if cr.level.value >= threshold.value]

    def _get_sort_key(self, check_result: CheckResult) -> Tuple[str, int, int]:
        if not check_result.metadata:
            return ("", 0, 0)
        return check_result.metadata.file_name, int(check_result.metadata.line), int(check_result.metadata.column)

    def sort_check_results(self) -> None:
        """Sort a list of check results by filenames (alphabetically) and also YAML line and column numbers."""
        self.check_results.sort(key=self._get_sort_key)

    def _format_text(self, disable_colors: bool = False, disable_docs_url: bool = False) -> str:
        """
        Format scan result as text.

        :param disable_colors: Disable output colors and styling
        :param disable_docs_url: Disable outputting URL to documentation
        :return: A formatted string
        """
        output = ""
        for result in self.check_results:
            output += result.construct_output(disable_colors, disable_docs_url) + "\n"

        def level_sort_key(level: DisplayLevel) -> int:
            return cast(int, level.value)

        worst_level = DisplayLevel.SUCCESS
        if len(self.check_results) > 0:
            worst_level = max((cr.level for cr in self.check_results), key=level_sort_key)
            output += "------------------------------------------------------------------------\n"

        time_message = f"Spotter took {self.summary.scan_time:.3f} s to scan your input."
        stats_message = f"It resulted in {self.summary.num_errors} error(s), {self.summary.num_warnings} " \
                        f"warning(s) and {self.summary.num_hints} hint(s)."
        overall_status_message = f"Overall status: {worst_level.name.upper()}"
        if not disable_colors:
            time_message = f"Spotter took {Style.BRIGHT}{self.summary.scan_time:.3f} s{Style.NORMAL} to scan " \
                           f"your input."
            stats_message = f"It resulted in {Style.BRIGHT + Fore.RED}{self.summary.num_errors} error(s)" \
                            f"{Fore.RESET + Style.NORMAL}, {Style.BRIGHT + Fore.YELLOW}{self.summary.num_warnings} " \
                            f"warning(s){Fore.RESET + Style.NORMAL} and {Style.BRIGHT}{self.summary.num_hints} " \
                            f"hint(s){Style.NORMAL}."

            if worst_level == DisplayLevel.ERROR:
                overall_status_message = \
                    f"Overall status: {Style.BRIGHT + Fore.RED}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"
            elif worst_level == DisplayLevel.WARNING:
                overall_status_message = \
                    f"Overall status: {Style.BRIGHT + Fore.YELLOW}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"
            elif worst_level == DisplayLevel.HINT:
                overall_status_message = \
                    f"Overall status: {Style.BRIGHT}{worst_level.name.upper()}{Style.NORMAL}"
            else:
                overall_status_message = \
                    f"Overall status: {Style.BRIGHT + Fore.GREEN}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"

        output += f"{time_message}\n{stats_message}\n{overall_status_message}"

        return output

    def _format_dict(self, disable_docs_url: bool = False) -> Dict[str, Any]:
        """
        Format scan result as Python dict.

        :param disable_docs_url: Disable outputting URL to documentation
        :return: A formatted string
        """
        check_result_outputs = []
        for result in self.check_results:
            metadata = result.metadata or ItemMetadata(file_name="", line=0, column=0)
            catalog_info = result.catalog_info
            suggestion_dict = {}
            if result.suggestion:
                suggestion_dict = {
                    "start_mark": result.suggestion.start_mark,
                    "end_mark": result.suggestion.end_mark,
                    "suggestion": result.suggestion.suggestion_spec,
                }

            check_result_outputs.append({
                "task_id": result.correlation_id,  # It is here because we want to be back compatible
                "file": metadata.file_name,
                "line": metadata.line,
                "column": metadata.column,
                "check_class": catalog_info.check_class,
                "event_code": catalog_info.event_code,
                "event_value": catalog_info.event_value,
                "event_message": catalog_info.event_message,
                "level": result.level.name.strip(),
                "message": result.message.strip(),
                "suggestion": suggestion_dict,
                "doc_url": None if disable_docs_url else result.doc_url,
                "correlation_id": result.correlation_id,
                "check_type": result.check_type.name.strip()
            })

        return {
            "uuid": self.uuid,
            "user": self.user,
            "user_info": self.user_info,
            "project": self.project,
            "environment": self.environment,
            "scan_date": self.scan_date,
            "subscription": self.subscription,
            "is_paid": self.is_paid,
            "summary": {
                "scan_time": self.summary.scan_time,
                "num_errors": self.summary.num_errors,
                "num_warnings": self.summary.num_warnings,
                "num_hints": self.summary.num_hints,
                "status": self.summary.status,
            },
            "check_results": check_result_outputs
        }

    def _format_json(self, disable_docs_url: bool = False) -> str:
        """
        Format scan result as JSON.

        :param disable_docs_url: Disable outputting URL to documentation
        :return: A formatted string
        """
        return json.dumps(self._format_dict(disable_docs_url), indent=2)

    def _format_yaml(self, disable_docs_url: bool = False) -> str:
        """
        Format scan result as YAML.

        :param disable_docs_url: Disable outputting URL to documentation
        :return: A formatted string
        """
        stream = StringIO()
        yaml.dump(
            self._format_dict(disable_docs_url), stream=stream, indent=2, default_flow_style=False, sort_keys=False
        )
        return stream.getvalue()

    def _format_junit_xml(self, disable_docs_url: bool = False) -> str:
        """
        Format scan result as JUnitXML.

        :param disable_docs_url: Disable outputting URL to documentation
        :return: A formatted string
        """
        try:
            junit_renderer = JUnitXml()
            return junit_renderer.render(self.check_results, disable_docs_url)
        except xml.parsers.expat.ExpatError as e:
            print(f"Error exporting JUnit XML: {e}.", file=sys.stderr)
            sys.exit(2)

    def format_output(self, output_format: OutputFormat, disable_colors: bool = False,
                      disable_docs_url: bool = False) -> str:
        """
        Format scan result.

        :param output_format: Target output format
        :param disable_colors: Disable output colors and styling
        :param disable_docs_url: Disable outputting URL to documentation
        :return: A formatted string
        """
        if output_format == OutputFormat.TEXT:
            return self._format_text(disable_colors, disable_docs_url)
        if output_format == OutputFormat.JSON:
            return self._format_json(disable_docs_url)
        if output_format == OutputFormat.YAML:
            return self._format_yaml(disable_docs_url)
        if output_format == OutputFormat.JUNIT_XML:
            return self._format_junit_xml(disable_docs_url)

        print(f"Error: unknown output format: {output_format}, "
              f"valid values are: {list(str(e) for e in OutputFormat)}.", file=sys.stderr)
        sys.exit(2)

    def apply_check_result_suggestions(self, scan_paths: List[Path]) -> None:
        """
        Automatically apply suggestions.

        :param scan_paths: A list of original paths to Ansible artifacts provided for scanning
        """
        all_suggestions = [cr.suggestion for cr in self.check_results if cr.suggestion is not None]

        # TODO: Remove when we find a solution for accessing original paths to Ansible artifacts provided for scanning
        for suggestion in all_suggestions:
            suggestion.file_parent = suggestion.file.parent
            for scan_path in scan_paths:
                if scan_path in (scan_path / suggestion.file).parents:
                    suggestion.file_parent = scan_path
                    break

        update_files(all_suggestions)


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new scan command parser to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "scan", help="Initiate Ansible scan", description="Initiate Ansible scan"
    )
    parser.add_argument(
        "--project-id", "-p", type=str, help="UUID of an existing project (default project from "
                                             "personal organization will be used if not specified)"
    )
    parser.add_argument(
        "--config", "-c", type=lambda p: Path(p).absolute(), help="Configuration file (as JSON/YAML)"
    )
    parser.add_argument(
        "--option", "-o", type=lambda s: s.strip().split("="), action="append", default=[], help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--ansible-version", type=str,
        choices=["2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "2.10", "2.11", "2.12", "2.13",
                 "2.14", "2.15"], metavar="[2.0, 2.15]",
        help="Target Ansible version to scan against (e.g., 2.14). If not specified, Spotter will try to discover the "
             "Ansible version installed on your system. If not found, all Ansible versions are considered for scanning."
    )
    parser.add_argument(
        "--include-values", action="store_true", help="Parse and upload values from Ansible task parameters"
    )
    parser.add_argument(
        "--upload-values", dest="include_values", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--include-metadata", action="store_true", help="Upload metadata (i.e., file names, line and column numbers)"
    )
    parser.add_argument(
        "--upload-metadata", dest="include_metadata", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--rewrite", "-r", action="store_true", help="Rewrite files with fixes"
    )
    parser.add_argument(
        "--display-level", "-l", type=DisplayLevel.from_string,
        choices=[DisplayLevel.HINT, DisplayLevel.WARNING, DisplayLevel.ERROR], default=DisplayLevel.HINT,
        help="Display only check results with specified level or greater "
             "(e.g., -l warning will show all warnings and errors, but suppress hints)"
    )
    parser.add_argument(
        "--profile", type=Profile.from_string,
        choices=list(Profile), default=Profile.DEFAULT,
        help="Set profile with selected set of checks to be used for scanning"
    )
    parser.add_argument(
        "--skip-checks", type=lambda s: [c for c in re.split(", | |,", s.strip()) if c], default=[],
        help="Skip checks with specified IDs (e.g., --skip-checks E101,H500,W1800)"
    )
    parser.add_argument(
        "--no-docs-url", action="store_true", help="Disable outputting URLs to documentation"
    )
    parser.add_argument(
        "--junit-xml", "-j", type=lambda p: Path(p).absolute(),
        help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--format", "-f", type=OutputFormat.from_string,
        choices=list(OutputFormat), default=OutputFormat.TEXT,
        help="Output format for the scan result"
    )
    parser.add_argument(
        "--output", type=lambda p: Path(p).absolute(),
        help="Output file path where the formatted scan result will be exported to"
    )
    import_export_group = parser.add_mutually_exclusive_group()
    import_export_group.add_argument(
        "--import-payload", "-i", type=lambda p: Path(p).absolute(),
        help="Path to the previously exported file to be sent for scanning"
    )
    import_export_group.add_argument(
        "--export-payload", "-e", type=lambda p: Path(p).absolute(),
        help="Output file path to export the locally scanned data without sending anything for scanning at the server"
    )
    parser.add_argument(
        "path", type=lambda p: Path(p).absolute(), nargs="*", help="Path to Ansible artifact or directory"
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace) -> None:
    # pylint: disable=too-many-branches,too-many-locals, too-many-statements
    """
    Execute callback for scan command.

    :param args: Argparse arguments
    """
    api_endpoint = args.endpoint or os.environ.get("SPOTTER_ENDPOINT", "")
    storage_path = args.storage_path or Storage.DEFAULT_PATH
    api_token = args.api_token or os.environ.get("SPOTTER_API_TOKEN")
    username = args.username or os.environ.get("SPOTTER_USERNAME")
    password = args.password or os.environ.get("SPOTTER_PASSWORD")
    scan_paths = args.path

    if args.import_payload and scan_paths:
        print("Error: the --import-payload is mutually exclusive with positional arguments.", file=sys.stderr)
        sys.exit(2)

    if args.export_payload and not scan_paths or (
            not args.export_payload and not args.import_payload and not scan_paths):
        print("Error: no paths provided for scanning.", file=sys.stderr)
        sys.exit(2)

    if args.export_payload and not args.include_metadata:
        print("Warning: exporting without the --include-metadata won't allow you to properly import payload.")
        yes = prompt_yes_no_question(default_yes_response=False)
        if not yes:
            sys.exit(0)

    config_vars = {}
    if args.option:
        print("Warning: the --option optional argument is deprecated. Use specific CLI optional arguments instead.")
        for key_value in args.option:
            if len(key_value) != 2:
                print(f"Error: '{'='.join(key_value)}' extra option is not specified as key=value.", file=sys.stderr)
                sys.exit(2)
            else:
                config_vars[key_value[0]] = key_value[1]
    if args.ansible_version:
        config_vars["ansible_version"] = args.ansible_version

    # workaround for a deprecated --junit-xml optional argument
    if args.junit_xml:
        print(f"Warning: the --junit-xml file.xml optional argument is deprecated. "
              f"Use --format {OutputFormat.JUNIT_XML} --output file.xml instead.")
        args.format = OutputFormat.JUNIT_XML
        args.output = args.junit_xml

    # ensure that colorized output is possible only when output is text-formatted and to be printed to the console
    if args.output or args.format != OutputFormat.TEXT:
        args.no_colors = True

    scan(api_endpoint, storage_path, api_token, username, password, args.no_colors, args.project_id, args.config,
         config_vars, args.include_values, args.include_metadata, args.rewrite, args.display_level, args.profile,
         args.skip_checks, args.no_docs_url, args.format, args.output, args.import_payload, args.export_payload,
         scan_paths)


# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
def scan(api_endpoint: str, storage_path: Path, api_token: Optional[str], username: Optional[str],
         password: Optional[str], no_colors: bool, project_id: Optional[str], config_path: Optional[Path],
         config_vars: Dict[str, Any], include_values: bool, include_metadata: bool, rewrite: bool,
         display_level: DisplayLevel, profile: Profile, skip_checks: List[str], no_docs_url: bool,
         output_format: OutputFormat, output_path: Optional[Path], import_payload: Optional[Path],
         export_payload: Optional[Path], scan_paths: List[Path]) -> None:
    """
    Scan Ansible content and return scan result.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param no_colors: Disable output colors
    :param project_id: UUID of an existing Steampunk Spotter project
    :param config_path: Path to configuration file
    :param config_vars: Configuration options and their values from optional arguments in a dict
    :param include_values: Parse and upload values from Ansible task parameters to the server
    :param include_metadata: Upload metadata (i.e., file names, line and column numbers) to the server
    :param config_vars: Configuration options in a dict
    :param include_values: Parse and upload values from Ansible task parameters to the server
    :param include_metadata: Upload metadata (i.e., file names, line and column numbers) to the server
    :param rewrite: Rewrite files with fixes
    :param display_level: Display only check results with specified level or greater
    :param profile: Profile with selected set of checks to be used for scanning
    :param skip_checks: List of check IDs for checks to be skipped
    :param no_docs_url: Disable outputting URLs to documentation
    :param output_format: for the scan result
    :param output_path: Output file path where the formatted scan result will be exported to
    :param import_payload: Path to the previously exported file to be sent for scanning
    :param export_payload: Path to export the locally scanned data without sending anything for scanning to the server
    :param scan_paths: Path to Ansible artifact or directory
    """
    # create and set environment
    # the order that we read configuration is the following (in each step we overwrite what the previous one has):
    # 1. local discovery (from user's current workspace)
    # 2. config file (JSON/YAML file provided after --config flag)
    # 3. options provided as key=value pairs to the scan command
    environment = Environment.from_local_discovery(scan_paths)
    if config_path:
        environment = environment.combine(Environment.from_config_file(config_path))
    if config_vars:
        environment = environment.combine(Environment.from_optional_arguments(config_vars))

    environment.cli_scan_args = {
        "parse_values": include_values,  # FIXME: Remove this deprecated option that is currently mandatory on backend.
        "include_values": include_values,
        "include_metadata": include_metadata,
        "rewrite": rewrite,
        "display_level": str(display_level),
        "profile": str(profile),
        "skip_checks": skip_checks,
    }
    if import_payload:
        parsing_result = ParsingResult(tasks=[], playbooks=[])
        scan_payload = ScanPayload.from_args(parsing_result, environment, include_metadata, import_payload)
        parsing_result.tasks = scan_payload.tasks
        parsing_result.playbooks = scan_payload.playbooks
    else:
        parsing_result = parse_ansible_artifacts(scan_paths, parse_values=bool(include_values))
        scan_payload = ScanPayload.from_args(parsing_result, environment, include_metadata, import_payload)

    if export_payload:
        scan_payload.to_json_file(export_payload)

        file_name = str(export_payload)
        try:
            # trim the part of the directory that is shared with CWD if this is possible
            file_name = str(Path(file_name).relative_to(Path.cwd()))
        except ValueError:
            pass

        print(f"Scan data saved to {file_name}.\nNote: this operation is fully offline. No actual scan was executed.")
        sys.exit(0)
    else:
        storage = Storage(storage_path)

        # TODO: extract this to a separate configuration component along with other configuration file options
        if not api_endpoint:
            if storage.exists("spotter.json"):
                storage_configuration_json = storage.read_json("spotter.json")
                api_endpoint = storage_configuration_json.get("endpoint", ApiClient.DEFAULT_ENDPOINT)
            else:
                api_endpoint = ApiClient.DEFAULT_ENDPOINT

        api_client = ApiClient(api_endpoint, storage, api_token, username, password)

        if project_id:
            scan_start_time = time.time()
            response = api_client.post(f"/v3/scans/?project={project_id}", payload=pydantic_encoder(scan_payload),
                                       timeout=120)
            scan_time = time.time() - scan_start_time
        else:
            scan_start_time = time.time()
            response = api_client.post("/v3/scans/", payload=pydantic_encoder(scan_payload), timeout=120)
            scan_time = time.time() - scan_start_time

        try:
            response_json = response.json()
        except json.JSONDecodeError as e:
            print(f"Error: scan result cannot be converted to JSON: {str(e)}", file=sys.stderr)
            sys.exit(2)

        scan_result = ScanResult.from_api_response(
            response_json,
            parsing_result.tasks,
            parsing_result.playbooks,
            scan_time)
        # TODO: Remove when scan API endpoint will be able to filter check results based on display level query param
        scan_result.filter_check_results(display_level)
        # TODO: figure out if we can sort returned check results by tasks line numbers and columns on the backend
        scan_result.sort_check_results()

        try:
            formatted_output = scan_result.format_output(output_format, no_colors, no_docs_url)
            if output_path:
                output_path.write_text(formatted_output, encoding="utf-8")
                print(f"Scan result exported to {output_path}.", file=sys.stderr)
            else:
                print(formatted_output)
        except TypeError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(2)

        if rewrite:
            scan_result.apply_check_result_suggestions(scan_paths)

        if len(scan_result.check_results) > 0:
            sys.exit(1)
