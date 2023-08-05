import os
import shutil
import subprocess
from typing import List, Optional

from lupin_grognard.core.tools.utils import check_if_file_exists, die, info, warn


class ClangFormatter:
    def __init__(self, name) -> None:
        self.name = name

    def format_c_cpp_files(self) -> None:
        if not self._check_clang_format_tool():
            die(
                msg=(
                    "could not find Clang-Format, use GROG_CLANG_FORMAT "
                    f"to configure the tool to be used (current value is '{self.name}')"
                )
            )
        code_directory = self._find_code_directory()
        if code_directory is None:
            die(msg="could not find a 'code' directory to be formatted")

        if not self._check_clang_format_file_configuration():
            warn(
                msg="could not find .clang-format file, please create one in the root path"
            )
        else:
            c_cpp_files = self._search_c_cpp_files(target_directory=code_directory)
            if len(c_cpp_files) == 0:
                info(msg="no C/C++ files found")
            else:
                for file in c_cpp_files:
                    self._format_files(file)

    def _check_clang_format_tool(self) -> bool | None:
        """Check if clang-format tool is installed on the system and available in the PATH"""
        path = shutil.which(self.name)
        return path is not None

    def _find_code_directory(self) -> Optional[str]:
        """Find the code directory in the project root"""
        code_directory = os.path.join(os.getcwd(), "code")
        if os.path.isdir(code_directory):
            return code_directory
        return None

    def _check_clang_format_file_configuration(self) -> bool:
        """Check if .clang-format file is present in the root path"""
        return check_if_file_exists(file=".clang-format")

    def _search_c_cpp_files(self, target_directory) -> List[str]:
        """Search all C/C++ files in the code directory and subdirectories
        return a list of C/C++ files paths"""
        file_extensions = [".h", ".cpp"]
        c_cpp_files = []
        for root, dirs, files in os.walk(target_directory):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    c_cpp_files.append(file_path.replace("\\", "/"))
        return c_cpp_files

    def _format_files(self, file: str) -> None:
        """Format the C/C++ files"""
        info(msg=f"Formatting C/C++ file: {file}")
        subprocess.run([self.name, "-i", file])
