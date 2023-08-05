import sys
from typing import List

from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.commit.commit_error import ErrorCount
from lupin_grognard.core.commit.commit_validator import CommitValidator
from lupin_grognard.core.config import MAJOR_COMMIT_TYPES


def check_max_allowed_major_commits(
    commits_string: List[str], major_commit_limit: int
) -> bool:
    """Check if the number of major commits in `commits_string` exceeds `major_commit_limit`.

    Args:
        commits_string (List[str]): The list of commit messages.
        major_commit_limit (int): The maximum number of major commits allowed.

    Returns:
        bool: True if the number of major commits is within the limit, else False.
    """
    if major_commit_limit == 0:  # --all option
        return True

    major_commit_count = 0
    commits = [Commit(c) for c in commits_string]
    for commit in commits:
        if commit.type in MAJOR_COMMIT_TYPES:
            major_commit_count += 1

    if major_commit_count > major_commit_limit:
        print(
            f"Error: found {major_commit_count} major commits to check in the "
            f"current branch while the maximum allowed number is {major_commit_limit}"
        )
        sys.exit(1)
    return True


def check_commit(commits: List, merge_option: int, permisive: bool = False) -> None:
    """
    check_commit performs validation checks on each commit.
    If merge_option is set to 0, the function checks that merge commits
    have approvers.
    If merge_option is 1, the function only validates the title for a merge,
    the title and the body of the commit if it is a simple commit.
    The function also calls the error_report method of the ErrorCount
    class to output any errors found during validation.
    If any errors are found, it will call sys.exit(1)
    Args:
        commits (List): List of commits to check
        merge_option (int): 0 or 1
    """
    error_counter = ErrorCount()
    for c in commits:
        commit = CommitValidator(commit=c, error_counter=error_counter)
        commit.perform_checks(merge_option)
    error_counter.error_report(permisive=permisive)
