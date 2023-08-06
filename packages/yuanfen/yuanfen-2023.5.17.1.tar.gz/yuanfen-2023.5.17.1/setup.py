import os

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yuanfen",
    version=os.environ.get("CI_COMMIT_TAG", "0.0.0"),
    author="Bean",
    author_email="bean@yuanfen.net",
    description="Yuanfen Python Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    install_requires=["pyyaml", "watchdog"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
