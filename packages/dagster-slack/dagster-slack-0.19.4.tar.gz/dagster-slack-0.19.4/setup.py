from pathlib import Path

from setuptools import find_packages, setup


def get_version():
    version = {}
    with open(Path(__file__).parent / "dagster_slack/version.py", encoding="utf8") as fp:
        exec(fp.read(), version)

    return version["__version__"]


ver = get_version()
# dont pin dev installs to avoid pip dep resolver issues
pin = "" if ver == "1!0+dev" else f"=={ver}"
setup(
    name="dagster-slack",
    version=ver,
    author="Elementl",
    author_email="hello@elementl.com",
    license="Apache-2.0",
    description="A Slack client resource for posting to Slack",
    url="https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-slack",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["dagster_slack_tests*"]),
    install_requires=[
        "dagster==1.3.4",
        "slack_sdk",
    ],
    zip_safe=False,
)
