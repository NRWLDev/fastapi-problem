"""Collection of useful commands for code management.

To view a list of available commands:

$ invoke --list
"""

import subprocess

import invoke


def current_branch():
    """Get the current branch from git cli using subprocess."""
    try:
        rev_parse_out = (
            subprocess.check_output(
                [
                    "git",
                    "rev-parse",
                    "--tags",
                    "--abbrev-ref",
                    "HEAD",
                ],
                stderr=subprocess.STDOUT,
            )
            .decode()
            .strip()
            .split("\n")
        )
    except subprocess.CalledProcessError as e:
        msg = "Could not get current branch name."
        raise invoke.exceptions.Exit(msg) from e

    return rev_parse_out[-1]


def enforce_branch(branch_name):
    """Enforce that the current branch matches the supplied branch_name."""
    if current_branch() != branch_name:
        msg = f"Command can not be run outside of {branch_name}."
        raise invoke.exceptions.Exit(msg)


@invoke.task
def install(context):
    """Install production requirements."""
    context.run("uv sync")


@invoke.task
def install_dev(context):
    """Install development requirements."""
    context.run("uv sync --all-extras")
    context.run("uv run pre-commit install")


@invoke.task
def check_style(context):
    """Run style checks."""
    context.run("ruff check .")


@invoke.task
def tests(context):
    """Run pytest unit tests."""
    context.run("pytest -x -s")


@invoke.task
def tests_coverage(context):
    """Run pytest unit tests with coverage."""
    context.run("pytest --cov -x --cov-report=xml")
