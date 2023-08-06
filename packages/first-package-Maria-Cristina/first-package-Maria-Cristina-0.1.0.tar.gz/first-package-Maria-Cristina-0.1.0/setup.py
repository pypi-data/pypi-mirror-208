from setuptools import setup

setup(
    name="first-package-Maria-Cristina",
    version="0.1.0",
    author="Maria",
    author_email="cristinamariab1998@gmail.com",
    packages=["my_own_package"],
    package_dir={"": "src"},
    include_package_data=True,
    description="my first package"
)
