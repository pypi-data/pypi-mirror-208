import os
from typing import List, Union

from lupin_grognard.core.tools.ros2.interfaces import Action, Msg, Srv
from lupin_grognard.core.tools.utils import die


def find_ros_packages(path: str) -> List[str]:
    """
    Retrieves the names of ROS packages present in the directory `path` and its subdirectories.

    :param path: Absolute path of the directory to explore.
    :type path: str
    :return: List of ROS package names, corresponding to directories containing a "package.xml" file.
    :rtype: List[str]
    """
    package_xml_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == "package.xml":
                package_xml_files.append(root)

    if len(package_xml_files) == 0:
        raise die(msg=f"No ROS package found in {path}")
    return package_xml_files


class PackageRos2:
    def __init__(self, package_path: str):
        self.package_path = package_path
        self.name = os.path.basename(package_path)
        self.description = self._get_package_description()

    def _get_package_description(self) -> str:
        package_xml = os.path.join(self.package_path, "package.xml")
        if os.path.isfile(package_xml):
            with open(package_xml, "r", encoding="utf-8") as f:
                for line in f:
                    if "<description>" in line:
                        description = line.split("<description>")[1].split(
                            "</description>"
                        )[0]
                        if description.endswith("."):
                            description = description.rstrip(".")
                        return description
        return ""

    def _find_files(self, file_type: str) -> List[Union[Msg, Srv, Action]]:
        """
        Finds all files of a given type in the package directory.

        :param file_type: Type of files to search for, either "msg", "srv", or "action".
        :type file_type: str
        :return: A list of parsed message/service/action objects corresponding to the files found.
        :rtype: List[Union[Msg, Srv, Action]]
        """
        files = []
        match_dict = {
            "msg": Msg,
            "srv": Srv,
            "action": Action,
        }
        file_dir = os.path.join(self.package_path, file_type)
        if os.path.isdir(file_dir):
            for file in os.listdir(file_dir):
                if file.endswith(f".{file_type}"):
                    files.append(os.path.join(file_dir, file))
        return [match_dict[file_type](self.name, file) for file in files]
