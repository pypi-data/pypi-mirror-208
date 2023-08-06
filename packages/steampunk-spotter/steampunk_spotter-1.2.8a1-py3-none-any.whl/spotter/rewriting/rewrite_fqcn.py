"""RewriteFqcn implementation."""

from typing import Optional

import re

from spotter.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class RewriteFqcn(RewriteBase):
    """RewriteFqcn implementation."""

    def get_regex(self, text_before: str) -> str:  # noqa: D102
        return rf"^(\s*({text_before}\s*):)"

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:  # noqa: D102
        suggestion_dict = suggestion.suggestion_spec
        part = self.get_context(content, suggestion)
        before = suggestion_dict["data"]["before"]
        after = suggestion_dict["data"]["after"]
        regex = self.get_regex(before)

        match = re.search(regex, part, re.MULTILINE)
        if match is None:
            print("Applying suggestion failed: could not find string to replace.")
            return None
        replacement = Replacement(content, suggestion, match, after)
        return replacement
