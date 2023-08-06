import os
from pathlib import Path

from setuptools import find_packages, setup


def get_version():
    if os.getenv("GITHUB_REF_TYPE", "branch") == "tag":
        return os.environ["GITHUB_REF_NAME"]

    version_file = here / "evacuator" / "VERSION"
    version = version_file.read_text().strip()

    build_num = os.environ.get("GITHUB_RUN_ID", "0")
    branch_name = os.environ.get("GITHUB_REF_NAME", "")

    if not branch_name:
        return version

    return f"{version}.dev{build_num}"


here = Path(__file__).parent.resolve()
long_description = here.joinpath("README.rst").read_text()

setup(
    name="evacuator",
    version=get_version(),
    description="Catch an exception and exit with an exit code",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="Apache License 2.0",
    license_files=("LICENSE.txt",),
    url="https://github.com/MobileTeleSystems/evacuator",
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    author="ONEtools Team",
    author_email="onetools@mts.ru",
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://evacuator.readthedocs.io",
        "Source": "https://github.com/MobileTeleSystems/evacuator",
        "CI/CD": "https://github.com/MobileTeleSystems/evacuator/actions",
        "Tracker": "https://github.com/MobileTeleSystems/evacuator/issues",
    },
)
