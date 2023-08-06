from setuptools import setup
from setuptools import find_packages

with open("Readme.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='steam-pysigma',
    version="2023.5.11",
    author="STEAM Team",
    author_email="steam-team@cern.ch",
    description="This is python wrapper of STEAM SIGMA code",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.cern.ch/steam/steam_pysigma",
    keywords={'STEAM', 'SIGMA', 'CERN'},
    install_requires=required,
    python_requires='>=3.8',
    package_data={'': ['steam-sigma-2023.4.12.jar', 'CFUN_mapping.csv']},
    include_package_data=True,
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3.8"
        ],
)
