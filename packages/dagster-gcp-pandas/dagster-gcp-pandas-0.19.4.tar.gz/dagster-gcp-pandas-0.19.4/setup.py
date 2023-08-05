from pathlib import Path
from typing import Dict

from setuptools import find_packages, setup


def get_version() -> str:
    version: Dict[str, str] = {}
    with open(Path(__file__).parent / "dagster_gcp_pandas/version.py", encoding="utf8") as fp:
        exec(fp.read(), version)

    return version["__version__"]


ver = get_version()
# dont pin dev installs to avoid pip dep resolver issues
pin = "" if ver == "1!0+dev" else f"=={ver}"
setup(
    name="dagster-gcp-pandas",
    version=ver,
    author="Elementl",
    author_email="hello@elementl.com",
    license="Apache-2.0",
    description="Package for storing Pandas DataFrames in GCP.",
    url="https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-gcp-pandas",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["dagster_gcp_pandas_tests*"]),
    include_package_data=True,
    install_requires=[
        "dagster==1.3.4",
        "dagster-gcp==0.19.4",
        "pandas<2",  # See: https://github.com/dagster-io/dagster/issues/13339
    ],
    extras_require={"test": ["pandas-gbq"]},
    zip_safe=False,
)
