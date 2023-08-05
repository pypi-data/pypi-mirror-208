from typing import List

from emoji import emojize

from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.config import EMOJI_CHECK, EMOJI_CROSS


class CommitReporter(Commit):
    def __init__(self, commit: str):
        super().__init__(commit=commit)

    def display_valid_title_report(self) -> None:
        print(emojize(f"{EMOJI_CHECK} Commit {self.hash[:6]}: {self.title}"))

    def display_invalid_title_report(self, error_message) -> None:
        print(emojize(f"{EMOJI_CROSS} Commit {self.hash[:6]}: {self.title}"))
        print(f"   {error_message}")

    def display_body_report(self, messages: List) -> None:
        print(emojize(f"{EMOJI_CROSS} Error in message discription:"))
        for message in messages:
            print(f"    {message}")

    def display_merge_report(self, approvers: List[str]):
        if len(approvers) > 1:
            many_approvers = ", ".join(approvers[:-1]) + " and " + approvers[-1]
            print(
                emojize(
                    f"{EMOJI_CHECK} Merge commit {self.hash[:6]}: Approvers: {many_approvers}"
                )
            )
        elif len(approvers) == 1:
            print(
                emojize(
                    f"{EMOJI_CHECK} Merge commit {self.hash[:6]}: Approver: {approvers[0]}"
                )
            )
        else:
            print(
                emojize(
                    f"{EMOJI_CROSS} Merge commit {self.hash[:6]}: No approver found"
                )
            )
        print(f"   - Merged on {self.author_date} by {self.author}, {self.author_mail}")
        print(
            f"   - Closes issue: {self.closes_issues if self.closes_issues else 'Not found'}"
        )
        print(f"   - Commit title: {self.title}")
