from setuptools import find_packages, setup

VERSION = "2.0.0"
DESCRIPTION = "API wrapper for POLAR TeamPro"

setup(
    name="polar_api",
    version=VERSION,
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.2",
        "isodate>=0.6.1",
        "pandas>=1.5.3",
        "requests-oauthlib>=1.3.1",
    ],
)
