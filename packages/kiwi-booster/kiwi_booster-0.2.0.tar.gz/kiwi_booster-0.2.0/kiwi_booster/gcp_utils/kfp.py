"""
wdasd
"""
import os
from pathlib import Path


def get_requirements():
    """
    Get a list of requirements from requirements.txt

    Returns:
        requirements (list): List of requirements
    """
    # Get the requirements file and read it line by line, save this into a list
    req_path = os.path.join(Path(__file__).parent, "requirements.txt")
    with open(req_path, "r") as file:
        content = file.read()

    lines = content.splitlines()
    requirements = [line for line in lines if line and not line.startswith("#")]

    return requirements
