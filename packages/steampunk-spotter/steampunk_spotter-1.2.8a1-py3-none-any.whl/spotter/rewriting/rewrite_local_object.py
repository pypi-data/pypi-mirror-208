"""RewriteLocalActionInline implementation."""

import re
from typing import Optional, Tuple

import yaml

from spotter.rewriting.rewrite_module_object import RewriteModuleObject
from spotter.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class RewriteLocalActionObject(RewriteBase):
    """RewriteLocalActionInline implementation."""

    def get_regex(self, text_before: str) -> str:  # noqa: D102
        return rf"^(\s*({text_before}\s*):)"

    def remove_module_row(self, content: str, suggestion: RewriteSuggestion) -> Tuple[str, RewriteSuggestion]:
        """
        Remove module line from content.

        :param content: Content that we want to rewrite
        :param suggestion: Suggestion object
        """
        module_replacement = RewriteModuleObject().get_replacement(content, suggestion)
        if module_replacement is None:
            module_name = suggestion.suggestion_spec["data"]["module_name"]
            print(f'Applying suggestion failed: could not find "{module_name}" to replace.')
            raise TypeError()
        rewrite_result = module_replacement.apply()
        suggestion.end_mark += rewrite_result.diff_size
        return rewrite_result.content, suggestion

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:  # noqa: D102
        # 1. Remove line "module: ..." from task arguments
        suggestion_data = suggestion.suggestion_spec["data"]
        content, suggestion = self.remove_module_row(content, suggestion)
        part = self.get_context(content, suggestion)

        # 2. Add "delegate_to": localhost
        index = self.get_indent_index(content, suggestion.start_mark)
        additional = " " * index + yaml.dump(suggestion_data["additional"][0])
        new_content = content + additional

        # 3. Replace "action:" with "<module_name>:"
        before = suggestion_data["original_module_name"]
        after = suggestion_data["module_name"]
        regex = self.get_regex(before)
        match = re.search(regex, part, re.MULTILINE)
        if match is None:
            print("Applying suggestion failed: could not find string to replace.")
            return None
        replacement = Replacement(new_content, suggestion, match, after)
        return replacement
