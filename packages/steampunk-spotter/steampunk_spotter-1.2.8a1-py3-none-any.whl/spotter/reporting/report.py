"""This is an interface for generating modular reports in various formats."""

import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
import itertools
from xml.dom import minidom
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    # cylic import
    from spotter.commands.scan import CheckResult


class ReportingInterface(ABC):
    """Interface for generating modular reports in various formats."""

    @abstractmethod
    def render(self, check_results: List["CheckResult"], disable_docs_url: bool) -> str:
        """Render the report based on the provided args as a string in the appropriate format."""


class JUnitXml(ReportingInterface):
    """Generate JUnit XML file."""

    def add_root_node(self) -> ET.Element:
        """Add root node to the XML report."""
        root = ET.Element("testsuites")
        return root

    def add_test_suite(self, root_node: ET.Element, name: str) -> ET.Element:
        """Add test suite to the XML report."""
        test_suite = ET.SubElement(root_node, "testsuite", name=name)
        return test_suite

    def add_test_case(self, test_suite: ET.Element, name: str, classname: str) -> ET.Element:
        """Add test case to the XML report."""
        test_case = ET.SubElement(test_suite, "testcase", name=name, classname=classname)
        return test_case

    def add_failure_info(self, test_case: ET.Element, message: str, typ: str) -> ET.Element:
        """Add failure info to the XML report."""
        error_case = ET.SubElement(test_case, "error", message=message, type=typ)
        return error_case

    def add_attribute(self, element: ET.Element, key: str, value: str) -> None:
        """Add attribute to the XML report."""
        element.set(key, value)

    def render(self, check_results: List["CheckResult"], disable_docs_url: bool) -> str:
        """Render the report."""
        root_node = self.add_root_node()
        get_check_class = lambda res: res.catalog_info.check_class  # pylint: disable=unnecessary-lambda-assignment
        for c_class, c_results in itertools.groupby(
                sorted(check_results, key=get_check_class),
                get_check_class):

            test_suite = self.add_test_suite(root_node, c_class)
            check_count = 0

            for result in c_results:
                test_case = self.add_test_case(
                    test_suite,
                    f"{result.catalog_info.event_code}-{result.catalog_info.event_value}[{check_count}]",
                    c_class
                )
                self.add_attribute(
                    test_case,
                    "id",
                    str(result.catalog_info.event_code)
                )
                self.add_attribute(
                    test_case,
                    "file",
                    str(result.metadata.file_name if result.metadata else "")
                )
                self.add_failure_info(
                    test_case,
                    result.construct_output(True, disable_docs_url),
                    result.level.name.upper(),
                )

                check_count += 1

            self.add_attribute(test_suite, "tests", str(check_count))
            self.add_attribute(test_suite, "errors", str(check_count))

        return str(minidom.parseString(
            ET.tostring(root_node, encoding="unicode", method="xml")
        ).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8"))
