import os

import typer
from dotenv import load_dotenv

from lupin_grognard.__init__ import __version__
from lupin_grognard.core.check import check_commit, check_max_allowed_major_commits
from lupin_grognard.core.commit.commit import Commit
from lupin_grognard.core.config import MAIN_BRANCHES_LIST
from lupin_grognard.core.doc_generator.changelog import Changelog
from lupin_grognard.core.doc_generator.reviewlog import Reviewlog
from lupin_grognard.core.doc_generator.ros2_docs import Ros2Docs
from lupin_grognard.core.format.clang_format import ClangFormatter
from lupin_grognard.core.format.cmake_format import CMakeFormatter
from lupin_grognard.core.git import Git
from lupin_grognard.core.tools.ros2.package import find_ros_packages

from .core.tools.utils import (
    configure_logging,
    die,
    display_number_of_commits_to_check,
    display_supported_commit_types,
    generate_commit_list,
    generate_commits_range_to_check,
    get_current_branch_name,
    info,
    is_main_branch,
)

load_dotenv()
GROG_BRANCHES = os.getenv("GROG_BRANCHES")
GROG_MAX_ALLOWED_COMMITS = os.getenv("GROG_MAX_ALLOWED_COMMITS")
GROG_DONT_CHECK_FOR_APPROVERS = os.getenv("GROG_DONT_CHECK_FOR_APPROVERS")
GROG_CLANG_FORMAT = os.getenv("GROG_CLANG_FORMAT")


cli = typer.Typer()


@cli.command()
def version():
    print(f"Version: {__version__}")


@cli.command()
def check_commits(
    all: bool = typer.Option(
        False, "--all", "-a", help="check all commits from initial commit"
    ),
    grog_max_allowed_commits: int = typer.Option(
        1, "--grog-max-allowed-commits", "-max", envvar="GROG_MAX_ALLOWED_COMMITS"
    ),
    grog_dont_check_for_approvers: int = typer.Option(
        0,
        "--grog-dont-check-for-approvers",
        "-dont-approvers",
        envvar="GROG_DONT_CHECK_FOR_APPROVERS",
        min=0,
        max=1,
    ),
    permisive: bool = typer.Option(
        False, "--permisive", "-p", help="ignore command failure"
    ),
):
    """
    Supported commit types: build(add|change|remove), bump, ci, deps(add|change|remove), docs, enabler,
    feat(add|change|remove), fix, refactor, test.
    Only one major commit types allowed per branch: "enabler", "feat", "fix" or "refactor".

    Check every commit message since the last "merge request" in any of the branches in the
    main_branches_list : "main", "master", "dev", "develop", "development"

    - With --all option :
    grog check-commits [--all or -a] to check all commits from initial commit.
    This option is automatically set if current branch is a main one.

    - With --permisisve option :
    grog check-commits [--permisive or -p] to ignore command failure.

    - With --grog-max-allowed-commits option :
    grog check-commits [--grog-max-allowed-commits or -max] {int} to set the maximum number
    of commits allowed to the branch.
    Example : grog check-commits --grog-max-allowed-commits 10

    - With --grog-dont-check-for-approvers option :
    by default, grog check commits will check for approvers in the Merge commit.
    grog check-commits [--grog-dont-check-for-approvers or -dont-approvers] 1 to disable option

    - With branches_name argument: grog check-commits "branch_1, branch_2..."

    You can set GROG_MAX_ALLOWED_COMMITS and GROG_DONT_CHECK_FOR_APPROVERS
    env var in .env, .gitlab-ci.yml, gitlab...
    """
    configure_logging()
    git = Git()
    current_branch_name = get_current_branch_name()

    if all or is_main_branch(current_branch_name, MAIN_BRANCHES_LIST):  # --all option
        git_log = git.get_log()
        grog_max_allowed_commits = 0
    else:
        git_log = git.get_log(max_line_count=50, first_parent=True)

    if git_log.stderr:
        die(f"git error {git_log.return_code}, {git_log.stderr}")

    commit_list = generate_commit_list(data=git_log.stdout)
    display_supported_commit_types()
    info(f"Current branch: {current_branch_name}")

    if all or is_main_branch(current_branch_name, MAIN_BRANCHES_LIST):  # --all option
        if is_main_branch(current_branch_name, MAIN_BRANCHES_LIST):
            info(
                msg=f"Processing all commits since current branch '{current_branch_name}' is a main one"
            )
        if check_max_allowed_major_commits(
            commits_string=commit_list, major_commit_limit=grog_max_allowed_commits
        ):
            display_number_of_commits_to_check(commit_list=commit_list)
            check_commit(
                commits=commit_list,
                merge_option=grog_dont_check_for_approvers,
                permisive=permisive,
            )
    else:
        commit_range_list_to_check = generate_commits_range_to_check(
            branch_list=MAIN_BRANCHES_LIST, commit_list=commit_list
        )
        if check_max_allowed_major_commits(
            commits_string=commit_range_list_to_check,
            major_commit_limit=grog_max_allowed_commits,
        ):
            display_number_of_commits_to_check(commit_list=commit_range_list_to_check)
            check_commit(
                commits=commit_range_list_to_check,
                merge_option=grog_dont_check_for_approvers,
                permisive=permisive,
            )


@cli.command()
def format(
    clang_format: str = typer.Option(
        "clang-format-14", "--clang-format", "-cf", envvar="GROG_CLANG_FORMAT"
    )
):
    """Format C/C++ files with clang-format
    You can set GROG_CLANG_FORMAT env var in order to configure the executable to be used
    """
    configure_logging()
    clang_formater = ClangFormatter(name=clang_format)
    clang_formater.format_c_cpp_files()

    cmake_formater = CMakeFormatter()
    cmake_formater.format_cmake_files()


@cli.command()
def changelog():
    """Generate changelog"""
    configure_logging()
    git_log = Git().get_log()
    if git_log.stderr:
        die(f"git error {git_log.return_code}, {git_log.stderr}")
    commit_list = generate_commit_list(data=git_log.stdout)
    commits = Commit.add_additional_commit_info(commit_list=commit_list)
    Changelog(commits=commits).generate()


@cli.command()
def reviewlog():
    """Generate REVIEWLOG.html"""
    configure_logging()
    git_log = Git().get_log()
    if git_log.stderr:
        die(f"git error {git_log.return_code}, {git_log.stderr}")
    commit_list = generate_commit_list(data=git_log.stdout)
    commits = Commit.add_additional_commit_info(commit_list=commit_list)
    Reviewlog(commits=commits).generate()


@cli.command()
def ros2docs(
    path: str = typer.Option(
        ..., "--path", "-p", help="path to search for ROS2 packages"
    )
):
    """Generate ROS2 documentation"""
    configure_logging()

    ros_packages = find_ros_packages(path)
    for path in ros_packages:
        api_doc = Ros2Docs(path=path)
        api_doc.generate_api_docs()
