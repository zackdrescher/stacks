"""Utility functions for the notebooks."""

import os
import pathlib


def check_dir() -> None:
    """Check if the current working directory is the root of the project."""
    if pathlib.Path.cwd().name == "notebooks":
        os.chdir("..")
