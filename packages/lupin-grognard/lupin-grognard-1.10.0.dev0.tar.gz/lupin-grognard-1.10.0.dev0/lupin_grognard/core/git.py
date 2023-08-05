import logging
import sys
from typing import List

from lupin_grognard.core.cmd import Command, run_command
from lupin_grognard.core.config import COMMIT_DELIMITER


class Git:
    def get_log(
        self, max_line_count: int = None, first_parent: bool = False
    ) -> Command:
        format: str = "hash>>%H%nauthor>>%cN%nauthor_mail>>%cE%nauthor_date>>%ct%ntitle>>%s%nbody>>%b<<body%n"
        delimiter = COMMIT_DELIMITER
        if first_parent:
            command = f'git log --first-parent --format="{format}"{delimiter}'
        else:
            command = f'git log --format="{format}"{delimiter}'
        if max_line_count:
            max_count = f"--max-count={max_line_count}"
            command = f"{command} {max_count}"
        return run_command(command=command)

    def get_branch_name(self) -> str:
        return run_command(command="git branch --show-current").stdout

    def get_remote_origin_url(self) -> str:
        c = run_command(command="git config --get remote.origin.url")
        if c.return_code != 0:
            self._git_error(
                msg=f"Git error while getting remote origin url: {c.stderr}"
            )
        gitlab_url = c.stdout
        if gitlab_url.startswith("https://gitlab.com/"):
            return gitlab_url[:-4] if gitlab_url.endswith(".git") else gitlab_url
        else:
            a = gitlab_url.find(":")
            if a != -1:
                gitlab_url = gitlab_url.replace(":", "/")
            gitlab_location = gitlab_url.find("@gitlab.com")
            gitlab_url = gitlab_url[gitlab_location + 1 :]
            gitlab_url = "https://" + gitlab_url
            return gitlab_url[:-4] if gitlab_url.endswith(".git") else gitlab_url

    def get_tags(self) -> List[List]:
        """Returns a list of tags with the following format:
        [
            ["tag_name", "tag_hash", "tag_date"],
            ["tag_name", "tag_hash", "tag_date"],
            ...
        ]
        """
        inner_delimiter = "---inner_delimiter---"
        dateformat = "%Y-%m-%d"
        formatter = (
            f'"%(refname:lstrip=2){inner_delimiter}'
            f"%(objectname){inner_delimiter}"
            f"%(creatordate:format:{dateformat}){inner_delimiter}"
            f'%(object)"'
        )
        c = run_command(command=f"git tag --format={formatter} --sort=-creatordate")

        if c.return_code != 0:
            self._git_error(msg=f"Git error while getting tags: {c.stderr}")
        if not c.stdout:
            return []

        tags_list = [line for line in c.stdout.splitlines()]
        return [tag.split(inner_delimiter)[:-1] for tag in tags_list]

    def get_parents(self, commit_hash: str) -> List[str]:
        c = run_command(command=f"git show --format=%P -s {commit_hash}")
        if c.return_code != 0:
            self._git_error(
                msg=f"Git error while getting parents of commit: {c.stderr}"
            )
        return c.stdout.split(" ")

    def get_first_commit_date(self) -> str:
        c = run_command(
            [
                "git",
                "log",
                "--reverse",
                "--format=%cd",
                "--date=format-local:%d/%m/%y %I:%M %p",
            ]
        )
        if c.return_code != 0:
            self._git_error(
                msg=f"Git error while getting first commit date: {c.stderr}"
            )
        return c.stdout.split("\n")[0]

    def get_last_commit_date(self) -> str:
        c = run_command(
            command=[
                "git",
                "log",
                "-1",
                "--pretty=format:%cd",
                "--date=format-local:%d/%m/%y %I:%M %p",
            ]
        )
        if c.return_code != 0:
            self._git_error(msg=f"Git error while getting last commit date: {c.stderr}")
        return c.stdout

    def _git_error(self, msg: str):
        logging.error(msg)
        sys.exit(1)
