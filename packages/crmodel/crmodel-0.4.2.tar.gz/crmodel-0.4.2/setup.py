import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# The requirements file
with open('requirements.txt') as f:
    required = f.read().splitlines()

# This call to setup() does all the work
setup(
    name="crmodel",
    version="0.4.2",
    description="crmodel is a python package that produces the crossroadsdesriber model from OpenStreetMap. See doi.org/10.5194/agile-giss-3-40-2022 for further informations.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jeremyk6/crmodel",
    author="Jérémy Kalsron",
    author_email="jeremy.kalsron@gmail.com  ",
    license="AGPL-3.0",
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=required,
    packages=["crmodel"],
    include_package_data=True,
)

