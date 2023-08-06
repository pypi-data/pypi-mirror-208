"""RewriteActionInline implementation."""

import re
from typing import Optional, Tuple

from spotter.rewriting.rewrite_module_inline import RewriteModuleInline
from spotter.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class RewriteActionInline(RewriteBase):
    """RewriteActionInline implementation."""

    def get_regex(self, text_before: str) -> str:  # noqa: D102
        return rf"^(\s*({text_before}\s*):)"

    def remove_module_name(self, content: str, suggestion: RewriteSuggestion) -> Tuple[str, RewriteSuggestion]:
        """
        Remove module name from content.

        :param content: Content that we want to rewrite
        :param suggestion: Suggestion object
        """
        module_replacement = RewriteModuleInline().get_replacement(content, suggestion)
        if module_replacement is None:
            module_name = suggestion.suggestion_spec["data"]["module_name"]
            print(f"Applying suggestion failed: could not find \"{module_name}\" to replace.")
            raise TypeError()
        rewrite_result = module_replacement.apply()
        suggestion.end_mark += rewrite_result.diff_size
        return rewrite_result.content, suggestion

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:  # noqa: D102
        suggestion_data = suggestion.suggestion_spec["data"]
        content, suggestion = self.remove_module_name(content, suggestion)
        part = self.get_context(content, suggestion)

        before = suggestion_data["original_module_name"]
        regex = self.get_regex(before)
        match = re.search(regex, part, re.MULTILINE)
        after = suggestion_data["module_name"]
        if match is None:
            print("Applying suggestion failed: could not find string to replace.")
            return None
        replacement = Replacement(content, suggestion, match, after)
        return replacement
