import re
from datetime import datetime
from typing import Dict, List, Tuple, Union

from lupin_grognard.core.config import INITIAL_COMMIT, PATTERN
from lupin_grognard.core.git import Git


class Commit:
    def __init__(self, commit: str):
        self.commit = commit
        self.associated_closed_issue = None
        self.associated_mr_approvers = None
        self.associated_mr_approvers_date = None
        self.parents = None

    @classmethod
    def add_additional_commit_info(cls, commit_list: List[str]) -> List["Commit"]:
        """
        Returns a list of Commit objects with additional information such as closed issues, approvers,
        and date it was approved for each commit from associated merge request

        :param commit_list: List of commits
        :return: List of Commit objects with additional information

        additional information:
            self.associated_closed_issue = None if merge commit else "1"
            self.associated_mr_approvers = None if merge commit else "John Doe"
            self.associated_mr_approvers_date = None if merge commit else "10/03/23 06:48 PM"
            self.parrents = ["hash1", "hash2"] if merge commit else ["hash1"]
        """
        commits = [cls(commit) for commit in commit_list]
        commits = cls._get_parents_for_commits(commits_list=commits)
        merge_commits_hash, merge_commits_mapping = cls._get_data_from_merge_commit(
            commits_list=commits
        )
        commits = cls._add_associated_data_to_commit_from_merge(
            merge_commits_hash=merge_commits_hash,
            merge_commits_mapping=merge_commits_mapping,
            commits_list=commits,
        )
        return commits

    @classmethod
    def _get_parents_for_commits(cls, commits_list: List["Commit"]) -> List["Commit"]:
        for commit in commits_list:
            commit.parents = Git().get_parents(commit_hash=commit.hash)
        return commits_list

    @classmethod
    def _get_data_from_merge_commit(
        cls, commits_list: List["Commit"]
    ) -> Tuple[List[str], Dict[str, Dict[str, Union[str, List[str], str]]]]:
        """
        Return a tuple containing a dictionary with information about merge commits and a list of merge commit hashes.

        The merge commit information dictionary has commit parent hash as keys, and the following information as values:
            - "closed_issue": L'id of the gitlab closed issue.
            - "approvers": A list of the usernames who approved the merge commit.
            - "date": The date the merge commit was approved.

        :param commits_list: A list of Commit objects.
        :type commits_list: List["Commit"]
        :return:
            - merge_commits_hash, merge_commits_mapping
            - A tuple containing the list of merge commit hashes and a merge commit information dictionary.
        :rtype: Tuple[List[str], Dict[str, Dict[str, Union[str, List[str], str]]]]
        """
        merge_commits_hash = []
        merge_commits_mapping = {}
        for commit in commits_list:
            if len(commit.parents) == 2:  # check if it is a merge commit
                merge_commits_hash.append(commit.hash)
                if commit.closes_issues:
                    merge_commits_mapping[commit.parents[1]] = {
                        "close_issue": commit.closes_issues[0],
                        "approvers": commit.approvers,
                        "date": commit.author_date,
                    }
        return merge_commits_hash, merge_commits_mapping

    @classmethod
    def _add_associated_data_to_commit_from_merge(
        cls,
        merge_commits_hash: List[str],
        merge_commits_mapping: Dict[str, Dict[str, Union[str, List[str], str]]],
        commits_list: List["Commit"],
    ) -> List["Commit"]:
        for commit in commits_list:
            if (
                len(commit.parents) == 1  # check if it is not a merge commit
                and commit.hash in merge_commits_mapping
                and commit.title not in INITIAL_COMMIT
            ):
                commit.associated_closed_issue = merge_commits_mapping[commit.hash][
                    "close_issue"
                ]
                commit.associated_mr_approvers = merge_commits_mapping[commit.hash][
                    "approvers"
                ]
                commit.associated_mr_approvers_date = merge_commits_mapping[
                    commit.hash
                ]["date"]
                if (
                    commit.parents[0] not in merge_commits_mapping
                    and commit.parents[0] not in merge_commits_hash
                ):  # the commit parent shares the same merge commit
                    merge_commits_mapping[commit.parents[0]] = merge_commits_mapping[
                        commit.hash
                    ]
        return commits_list

    @property
    def hash(self) -> str:
        return self._extract(start="hash>>")

    @property
    def author(self) -> str:
        return self._extract(start="author>>")

    @property
    def author_mail(self) -> str:
        return self._extract(start="author_mail>>")

    @property
    def author_date(self) -> str:
        timestamp = self._extract(start="author_date>>")
        date_object = datetime.fromtimestamp(int(timestamp))
        return date_object.strftime("%d/%m/%y %I:%M %p")

    @property
    def title(self) -> str:
        return self._extract(start="title>>")

    @property
    def title_without_type_scope(self) -> str:
        """Returns commit title without type and scope"""
        start = self.title.find(":") + 1
        return self.title[start:].strip().capitalize()

    @property
    def type(self) -> str | None:
        """Returns the conventional commit type if present"""
        match = re.match(PATTERN, self.title)
        return match.groups()[0] if match else None

    @property
    def scope(self) -> str | None:
        """Returns the conventional commit scope if present"""
        match = re.match(PATTERN, self.title)
        return match.groups()[1] if match else None

    @property
    def body(self) -> List[str] | None:
        body = self._extract(start="body>>", end="<<body")
        if body == "":
            return None
        return [message for message in body.split("\n") if len(message) > 0]

    @property
    def closes_issues(self) -> List | None:
        """Returns the list of issues closed by the commit"""
        if self.body:
            for line in self.body:
                if line.startswith("Closes #"):  # Closes #465, #190 and #400
                    return re.findall(r"#(\d+)", line)  # ['465', '190', '400']
        return None

    @property
    def approvers(self) -> List[str]:
        approvers = []
        if self.body:
            for line in self.body:
                if line.startswith("Approved-by: "):
                    approvers.append(line.split("Approved-by: ")[1])
            return approvers
        return list()

    def _extract(self, start: str, end: str = "\n") -> str:
        start_index = self.commit.find(start) + len(start)
        return self.commit[start_index : self.commit.find(end, start_index)]
