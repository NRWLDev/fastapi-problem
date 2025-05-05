"""Collection of useful commands for code management.

To view a list of available commands:

$ invoke --list
"""

import invoke


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
