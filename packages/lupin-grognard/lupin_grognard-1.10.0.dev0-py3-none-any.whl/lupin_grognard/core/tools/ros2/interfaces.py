import os

from .parser import (
    ActionSpecification,
    MessageSpecification,
    ServiceSpecification,
    extract_file_level_comments,
    parse_action_file,
    parse_message_file,
    parse_service_file,
)


class InterfaceRos2:
    def __init__(self, package_name: str, path: str):
        self.package_name = package_name
        self.path = path

    @property
    def name(self) -> str:
        suffixes = (".msg", ".srv", ".action")
        for suffix in suffixes:
            if self.path.endswith(suffix):
                return os.path.basename(self.path)[: -len(suffix)]


class Msg(InterfaceRos2):
    def __init__(self, package_name: str, path: str):
        super().__init__(package_name, path)

    def parse_message_file(self) -> MessageSpecification:
        return parse_message_file(self.package_name, self.path)

    @property
    def comment(self) -> str:
        """
        The comment block at the top of the message file.
        """
        parsed_message = self.parse_message_file()
        comments_list = parsed_message.annotations.get("comment", [])
        return "\n".join(comments_list)

    @property
    def code(self) -> str:
        """
        The code block after the comment block in the message file.
        """
        with open(self.path, "r", encoding="utf-8") as f:
            message_string = f.read()
        code_list = extract_file_level_comments(message_string=message_string)[1]
        return "\n".join(code_list).strip()


class Srv(InterfaceRos2):
    def __init__(self, package_name: str, path: str):
        super().__init__(package_name, path)

    def parse_service_file(self) -> ServiceSpecification:
        return parse_service_file(self.package_name, self.path)

    @property
    def comment(self) -> str:
        """
        The comment block at the top of the service file.
        """
        parsed_service = self.parse_service_file()
        comments_list = parsed_service.request.annotations.get("comment", [])
        return "\n".join(comments_list)


class Action(InterfaceRos2):
    def __init__(self, package_name: str, path: str):
        super().__init__(package_name, path)

    def parse_action_file(self) -> ActionSpecification:
        return parse_action_file(self.package_name, self.path)

    @property
    def comment(self) -> str:
        """
        The comment block at the top of the action file.
        """
        parsed_action = self.parse_action_file()
        comments_list = parsed_action.goal.annotations.get("comment", [])
        return "\n".join(comments_list)
