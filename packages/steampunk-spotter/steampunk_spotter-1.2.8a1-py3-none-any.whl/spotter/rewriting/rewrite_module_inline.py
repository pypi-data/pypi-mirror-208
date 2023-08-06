"""RewriteModuleInline implementation."""

import re
from typing import Optional

from spotter.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class RewriteModuleInline(RewriteBase):
    """RewriteModuleInline implementation."""

    def get_regex(self, text_before: str) -> str:  # noqa: D102
        return rf"((\s{text_before}|{text_before}\s))"

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:  # noqa: D102
        suggestion_data = suggestion.suggestion_spec["data"]
        part = self.get_context(content, suggestion)
        before = suggestion_data["module_name"]
        regex = self.get_regex(before)
        match = re.search(regex, part, re.MULTILINE)
        after = ""
        if match is None:
            print("Applying suggestion failed: could not find string to replace.")
            return None
        replacement = Replacement(content, suggestion, match, after)
        return replacement
