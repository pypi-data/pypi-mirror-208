import sys

from lupin_grognard.core.config import (
    BODY_FAILED,
    FAILED,
    MERGE_FAILED,
    SUCCESS,
    TITLE_FAILED,
)
from lupin_grognard.core.tools.utils import warn


class ErrorCount:
    def __init__(self):
        self.body_error = 0
        self.title_error = 0
        self.merge_error = 0

    def increment_body_error(self):
        self.body_error += 1

    def increment_title_error(self):
        self.title_error += 1

    def increment_merge_error(self):
        self.merge_error += 1

    def error_report(self, permisive: bool):
        if not (self.title_error + self.body_error + self.merge_error):
            print(SUCCESS)
        else:
            print(FAILED)
            print(
                f"Errors found: {self.title_error + self.body_error + self.merge_error}"
            )
            if self.title_error > 0:
                print(TITLE_FAILED)
            if self.body_error > 0:
                print(BODY_FAILED)
            if self.merge_error > 0:
                print(MERGE_FAILED)

            if permisive:
                warn(msg="ignoring command failure because running in permissive mode")
                sys.exit(0)
            else:
                sys.exit(1)
