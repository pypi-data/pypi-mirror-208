import sys

import os
import pathlib
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.sdist import sdist
from setuptools import setup, find_packages
from subprocess import check_call

if sys.version_info < (3, 0):
    sys.exit(
        """
######################################
# Python 3 is needed #
######################################
"""
    )

_version = "0.6.0-1"

HERE = pathlib.Path(__file__).parent


# USING SUBMODULE https://oak-tree.tech/blog/python-packaging-primer
def gitcmd_update_submodules():
    '''    Check if the package is being deployed as a git repository. If so, recursively
        update all dependencies.

        @returns True if the package is a git repository and the modules were updated.
            False otherwise.
    '''
    if os.path.exists(os.path.join(HERE, '.git')):
        check_call(['git', 'submodule', 'update', '--init', '--recursive'])
        return True

    return False


class gitcmd_develop(develop):
    '''    Specialized packaging class that runs git submodule update --init --recursive
        as part of the update/install procedure.
    '''
    def run(self):
        gitcmd_update_submodules()
        develop.run(self)


class gitcmd_install(install):
    '''    Specialized packaging class that runs git submodule update --init --recursive
        as part of the update/install procedure.
    '''
    def run(self):
        gitcmd_update_submodules()
        install.run(self)


class gitcmd_sdist(sdist):
    '''    Specialized packaging class that runs git submodule update --init --recursive
        as part of the update/install procedure;.
    '''
    def run(self):
        gitcmd_update_submodules()
        sdist.run(self)


# print("TO COPY", find_packages("src", exclude=["*.tests", "*.tests.*", "tests.*", "tests"]))

setup(
    cmdclass={
        'develop': gitcmd_develop,
        'install': gitcmd_install,
        'sdist': gitcmd_sdist,
    },
    name="navabilitysdk",
    version=_version,
    license="Apache-2.0",
    author="NavAbility",
    author_email="info@navability.io",
    packages=find_packages("src", exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={"": "src"},
    package_data={"sdkCommonGQL": ["*.toml",],},
    # data_files=[('sdkCommonGQL',['*.toml',]),],
    include_package_data=True,
    # entry_points={"console_scripts": ["navability = navability.main:cli"]},
    python_requires=">=3.8",
    download_url=f"https://github.com/NavAbility/NavAbilitySDK.py/archive/refs/tags/v{_version}.tar.gz",  # noqa: E501, B950
    long_description="""NavAbility SDK: Access NavAbility Cloud factor graph features from Python.
Note that this SDK and the related API are in beta. Please let us know if you have any issues at info@navability.io.""",
    install_requires=[
        "click==8.0.2",
        "gql[all]==3.0.0a6",
        "ipython==8.2.0",
        "marshmallow==3.14.0",
        "numpy>=1.21",
        "nest-asyncio>=1.5",
        # Dev/test dependencies
        "black==22.3.0",  # REF: https://github.com/psf/black/issues/2634
        "flake8==4.0.1",
        "pytest==6.2.5",
        "pytest-asyncio==0.18.1",
        "pyyaml==6.0",
    ],
)
