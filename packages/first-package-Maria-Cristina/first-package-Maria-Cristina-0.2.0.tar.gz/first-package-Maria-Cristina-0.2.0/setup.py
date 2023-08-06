from setuptools import setup
from pathlib import Path

d = Path(__file__).parent
description = (d / "README.md").read_text()

setup(
    name="first-package-Maria-Cristina",
    version="0.2.0",
    author="Maria",
    author_email="cristinamariab1998@gmail.com",
    packages=["my_own_package"],
    package_dir={"": "src"},
    include_package_data=True,
    description="my first package",
    long_description=description,
    long_description_content_type="text/markdown"
)
