from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="floating",
    description="Calculates floating precision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.0.1",
    url="https://github.com/mreiche/python-floating",
    author="Mike Reiche",
    py_modules=['floating'],
    install_requires=[],
)
