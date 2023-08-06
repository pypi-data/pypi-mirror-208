import re

from setuptools import find_packages
from setuptools import setup

import versioneer

setup(
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        r
        for r in open("requirements.in").read().splitlines()
        if r and not re.match(r"\s*\#", r[0])
    ],
    extras_require={
        "dev": [
            r
            for r in open("requirementsDev.in").read().splitlines()
            if r and not re.match(r"\s*\#", r)
        ]
    },
)
