import os
import unicodedata
from typing import Dict, List

from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.doc_generator.jinja_generator import JinjaGenerator
from lupin_grognard.core.git import Git
from lupin_grognard.core.tools.utils import info


class Reviewlog(JinjaGenerator):
    def __init__(self, commits: List[Commit]):
        self.commits = commits
        self.git = Git()

    def generate(self):
        project_url = self.git.get_remote_origin_url()
        project_name = project_url.split("/")[-1]
        info(msg=f"Collecting approvers report from {project_name}")
        approvers_report = self._get_approvers_report()
        approvers_participants = self._get_approvers_participants(approvers_report)
        self._generate_file(
            path=os.getcwd(),
            file_name="REVIEWLOG",
            file_extension=".html",
            context={
                "approvers_report": approvers_report,
                "project_name": project_name,
                "project_url": project_url,
                "participants": approvers_participants,
            },
        )

    def _generate_file(
        self, path: str, file_name: str, file_extension: str, context: Dict
    ) -> None:
        return super()._generate_file(path, file_name, file_extension, context)

    def _normalize_string(self, string: str) -> str:
        return (
            unicodedata.normalize("NFD", string)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )

    def _remove_duplicate_participants(self, participants: List[str]) -> List[str]:
        """
        Remove duplicate participants from a list of participants
        :param participants: List of participants
        :return: List of participants with accent without duplicates

        Example:
        ["Cédric", "Cedric", "Aurelien", "Aurélien", "John Doe", "John Doe"] -> ["Aurélien", "Cédric", "John Doe"]
        """
        result = []
        participants_with_accents = set()
        participants_without_accents = set()
        for participant in participants:
            string_without_accents = self._normalize_string(participant)
            if string_without_accents == participant:
                participants_without_accents.add(participant)
            else:
                participants_with_accents.add(participant)

        for participant in participants_with_accents:
            normalized_string = self._normalize_string(participant)
            if normalized_string in participants_without_accents:
                participants_without_accents.remove(normalized_string)

        result = list(participants_without_accents)
        result.extend((list(participants_with_accents)))
        result = sorted(result)
        return [participant.title() for participant in result]

    def _get_approvers_participants(self, approvers_report) -> List[str]:
        approvers_participants = []
        for report in approvers_report:
            autor = report.get("autor")
            approvers = report.get("approvers", [])
            if autor not in approvers_participants:
                approvers_participants.append(autor)
            for approver in approvers:
                if approver not in approvers_participants:
                    approvers_participants.append(approver)
        return self._remove_duplicate_participants(approvers_participants)

    def _get_name_without_mail_for_approvers(self, approvers: List[str]) -> List[str]:
        approvers_name = []
        for approver in approvers:
            start_mail = approver.find("<")
            if start_mail != -1:
                approver_without_mail = approver[:start_mail].strip()
                approvers_name.append(approver_without_mail)
            else:
                approvers_name.append(approver)
        return approvers_name

    def _get_approvers_report(self) -> List[dict]:
        approvers_report = []
        for commit in self.commits:
            if commit.associated_closed_issue:
                info(
                    msg=f"Collecting report for issue {commit.associated_closed_issue}"
                )
                approvers = self._get_name_without_mail_for_approvers(
                    commit.associated_mr_approvers
                )
                approvers_report.append(
                    {
                        "commit_hash": commit.hash[:6],
                        "gitlab_issue_id": commit.associated_closed_issue,
                        "title": commit.title,
                        "description": commit.body,
                        "autor": commit.author,
                        "date": commit.author_date,
                        "approvers": approvers,
                        "approver_date": commit.associated_mr_approvers_date,
                    }
                )
        return approvers_report
