import os
import shutil
import subprocess
from typing import List

from lupin_grognard.core.tools.utils import check_if_file_exists, die, info, warn


class CMakeFormatter:
    def format_cmake_files(self) -> None:
        if not self._check_cmake_format_tool():
            die(
                msg="could not find CMake-Format, install it from https://github.com/cheshirekow/cmake_format"
            )
        if not self._check_cmake_format_yaml_file_exist():
            warn(
                msg="could not find .cmake-format.yaml file, please create one in the root path"
            )
        else:
            cmake_files = self._find_cmake_files()
            if len(cmake_files) == 0:
                info(msg="no CMake files found")
            else:
                for file in cmake_files:
                    self._format_file(file)

    def _check_cmake_format_tool(self) -> str | None:
        """Check if cmake-format tool is installed on the system and available in the PATH"""
        path = shutil.which("cmake-format")
        return path is not None

    def _check_cmake_format_yaml_file_exist(self) -> bool:
        """Check if a .cmake-format.yaml file is present in the root path"""
        return check_if_file_exists(file=".cmake-format.yaml")

    def _find_cmake_files(self) -> List[str]:
        """Find all CMake files in the root, code and cmake directories"""
        cmake_files = []
        if os.path.exists(os.path.join(os.getcwd(), "CMakeLists.txt")):
            self._append_file_path(
                root=os.getcwd(), file="CMakeLists.txt", cmake_files=cmake_files
            )

        for dir in ["code", "cmake"]:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file == "CMakeLists.txt" or file.endswith(".cmake"):
                        self._append_file_path(
                            root=root, file=file, cmake_files=cmake_files
                        )
        return cmake_files

    def _append_file_path(self, root: str, file: str, cmake_files: List[str]) -> None:
        """Append the CMake file path to the list of CMake files"""
        cmake_file_path = os.path.join(root, file)
        cmake_file_path_slash = cmake_file_path.replace("\\", "/")
        cmake_files.append(cmake_file_path_slash)

    def _format_file(self, file: str) -> None:
        """Format the CMake files using cmake-format tool"""
        info(msg=f"Formatting CMake file: {file}")
        subprocess.run(["cmake-format", "-i", file])
