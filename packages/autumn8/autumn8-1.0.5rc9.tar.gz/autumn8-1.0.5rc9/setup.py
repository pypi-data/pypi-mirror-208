from pathlib import Path

from setuptools import find_namespace_packages, setup

from autumn8.common._version import __version__

this_directory = Path(__file__).parent
readme_content = (this_directory / "README.md").read_text()

# all the configuration is now handled in pyproject.toml
setup()
