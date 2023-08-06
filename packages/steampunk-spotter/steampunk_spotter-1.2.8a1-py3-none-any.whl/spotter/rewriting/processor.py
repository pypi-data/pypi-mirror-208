"""Entry point of rewriting functionality."""
from typing import Optional, List, cast

import os
import itertools

import yaml

from spotter.rewriting.rewrite_action_inline import RewriteActionInline
from spotter.rewriting.rewrite_action_object import RewriteActionObject
from spotter.rewriting.rewrite_always_run import RewriteAlwaysRun
from spotter.rewriting.rewrite_fqcn import RewriteFqcn
from spotter.rewriting.rewrite_inline import RewriteInline
from spotter.rewriting.rewrite_local_action_inline import RewriteLocalActionInline
from spotter.rewriting.rewrite_local_object import RewriteLocalActionObject
from spotter.rewriting.models import Replacement, RewriteResult
from spotter.rewriting.models import RewriteSuggestion


class RewriteProcessor:
    """Factory that will use correct implementation depending on 'action' inside 'suggestion'."""

    rewriter_mapping = {
        "FIX_FQCN": RewriteFqcn,
        "FIX_REDIRECT": RewriteFqcn,
        "FIX_INLINE": RewriteInline,
        "FIX_ALWAYS_RUN": RewriteAlwaysRun,
        "FIX_ACTION_INLINE": RewriteActionInline,
        "FIX_ACTION_OBJECT": RewriteActionObject,
        "FIX_LOCAL_ACTION_OBJECT": RewriteLocalActionObject,
        "FIX_LOCAL_ACTION_INLINE": RewriteLocalActionInline,
    }

    @classmethod
    def execute(cls, content: str, suggestion: RewriteSuggestion) -> Optional[RewriteResult]:
        """
        Update task content.

        :param content: Old task content
        :param suggestion: Suggestion object for a specific task
        :return: Tuple with updated content and content length difference, or none if matching failed.
        """
        replacement = cls.get_replacement(content, suggestion)
        if not replacement:
            return RewriteResult(content=content, diff_size=0)

        return replacement.apply()

    @classmethod
    def multi_execute(cls, content: str, suggestions: List[RewriteSuggestion]) -> RewriteResult:
        """
        Update task content with multiple suggestions.

        :param content: Old task content
        :param suggestions: List of suggestions of specific tasks
        :return: List of tuples with updated content and content length difference, or none if matching failed
        """
        suggestion_start_position = -1
        previous_suggestion = None
        for suggestion in suggestions:
            len_before = len(content)
            if suggestion_start_position == suggestion.start_mark and previous_suggestion:
                suggestion.end_mark = previous_suggestion.end_mark
            suggestion_start_position = suggestion.start_mark

            replacement = cls.get_replacement(content, suggestion)
            if replacement is None:
                raise TypeError()
            rewrite_result = replacement.apply()
            new_content, _ = rewrite_result.content, rewrite_result.diff_size
            length_diff = len(new_content) - len_before
            suggestion.end_mark = suggestion.end_mark + length_diff
            previous_suggestion = suggestion
            content = new_content

        return RewriteResult(content=content, diff_size=length_diff)

    @classmethod
    def get_replacement(cls, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:
        """
        Get replacement according to action.

        :param content: Old task content
        :param suggestion: Suggestion object for a specific task
        """
        suggestion_dict = suggestion.suggestion_spec
        action = cast(str, suggestion_dict.get("action"))

        rewriter_class = cls.rewriter_mapping.get(action)
        if not rewriter_class:
            print(f"Unknown mapping: {action}")
            return None

        rewriter = rewriter_class()  # type: ignore[abstract]  # we assume the mapping only contains implementations
        replacement = rewriter.get_replacement(content, suggestion)
        return replacement


def update_files(suggestions: List[RewriteSuggestion]) -> None:  # pylint: disable=too-many-locals
    """
    Update files by following suggestions.

    :param suggestions: List of suggestions as Suggestion objects
    """
    get_file_func = lambda x: x.file  # pylint: disable=unnecessary-lambda-assignment
    files = [(file, list(suggests)) for file, suggests in itertools.groupby(suggestions, get_file_func)]

    get_inode_func = lambda x: os.stat(x[0]).st_ino  # pylint: disable=unnecessary-lambda-assignment
    inodes = [next(group) for _, group in itertools.groupby(sorted(files, key=get_inode_func), get_inode_func)]

    requirements_update_suggestions = set()
    for file, suggests in inodes:
        # python sort is stable, so items with same start mark, should stay in same order
        suggestions_reversed = sorted(suggests, key=lambda x: -x.start_mark)
        suggestions_requirements = \
            [x for x in suggestions_reversed if x.suggestion_spec.get("action") == "FIX_REQUIREMENTS"]
        suggestions_items = \
            [x for x in suggestions_reversed if x.suggestion_spec.get("action") != "FIX_REQUIREMENTS"]

        with file.open("r", encoding="utf-8") as f:
            content = f.read()

        end_content = content
        try:
            #  Requirements
            for suggestion in suggestions_requirements:
                suggestion_dict = suggestion.suggestion_spec
                if suggestion_dict.get("action") == "FIX_REQUIREMENTS":
                    collection_name = suggestion_dict["data"]["collection_name"]
                    collection_version = suggestion_dict["data"]["version"]
                    # TODO: Update path when we are able to get it from scan input or scan result
                    requirements_yml_path = suggestion.file_parent / "requirements.yml"
                    requirements_update_suggestions.add((requirements_yml_path, collection_name, collection_version))
                    continue

            # other
            rewrite_result = RewriteProcessor.multi_execute(end_content, suggestions_items)
            if rewrite_result is None:
                continue
            end_content = rewrite_result.content
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error when rewriting {file}: {e}")

        if end_content != content:
            with file.open("w", encoding="utf-8") as f:
                f.write(end_content)

    # TODO: Consider updating this when we will be updating detection and rewriting of collection requirements
    for (
            requirements_yml_path,
            collection_name,
            collection_version,
    ) in requirements_update_suggestions:
        with requirements_yml_path.open("a+", encoding="utf-8") as requirements_file:
            requirements_file.seek(0)
            try:
                data = yaml.safe_load(requirements_file)
            except yaml.YAMLError:
                # overwrite erroneous requirement file
                data = None
            if not data:
                data = {}
            if not isinstance(data, dict):
                # should we overwrite in this case as well?
                continue
            if "collections" not in data or ("collections" in data and data["collections"] is None):
                data["collections"] = []

            data["collections"].append({"name": collection_name, "version": collection_version})
            requirements_file.seek(0)
            requirements_file.truncate()
            requirements_file.write(yaml.dump(data, default_flow_style=False))
