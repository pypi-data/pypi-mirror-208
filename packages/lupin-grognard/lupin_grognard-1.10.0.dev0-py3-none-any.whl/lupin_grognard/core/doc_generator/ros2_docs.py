import os
from typing import Dict

from lupin_grognard.core.doc_generator.jinja_generator import JinjaGenerator
from lupin_grognard.core.tools.ros2.package import PackageRos2


class Ros2Docs(JinjaGenerator):
    def __init__(self, path: str):
        self.path = path
        self.package = PackageRos2(package_path=path)

    def get_package_info(self) -> Dict:
        """
        Returns a dictionary with the following keys:
        - package: PackageRos2 object
        - msgs: a list of Msg objects
        - srvs: a list of Srv objects
        - actions: a list of Action objects

        :return: a dictionary with the package info
        :rtype: Dict"""
        package = self.package
        return {
            "package": package,
            "msgs": package._find_files(file_type="msg"),
            "srvs": package._find_files(file_type="srv"),
            "actions": package._find_files(file_type="action"),
        }

    def generate_api_docs(self) -> None:
        if not self._is_docs_dir_exists():
            os.mkdir(os.path.join(self.path, "docs"))

        self._generate_file(
            path=os.path.join(self.path, "docs"),
            file_name="RosApi",
            file_extension=".md",
            context=self.get_package_info(),
        )

    def _is_docs_dir_exists(self) -> bool:
        return os.path.isdir(os.path.join(self.path, "docs"))

    def _generate_file(
        self, path: str, file_name: str, file_extension: str, context: Dict
    ) -> None:
        return super()._generate_file(path, file_name, file_extension, context)
