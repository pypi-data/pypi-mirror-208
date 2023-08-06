"""RewriteModuleObject implementation."""

import re
from typing import Optional

from spotter.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class RewriteModuleObject(RewriteBase):
    """RewriteModuleObject implementation."""

    def get_regex(self, text_before: str) -> str:  # noqa: D102
        return rf"((\n\s+{text_before}:\s[^\n]+))"

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:  # noqa: D102
        part = self.get_context(content, suggestion)
        before = "module"
        regex = self.get_regex(before)
        match = re.search(regex, part)
        after = ""
        if match is None:
            print("Applying suggestion failed: could not find string to replace.")
            return None
        replacement = Replacement(content, suggestion, match, after)
        return replacement
