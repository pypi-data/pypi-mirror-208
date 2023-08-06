from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
with open(this_directory / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gy_multiprocessing",
    version="0.2.4.3",
    author="Guangyu He",
    author_email="me@heguangyu.net",
    description="Run function in multiple processes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guangyu-he/gy-multiprocessing",
    install_requires=[],
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    tests_require=["pytest"]
)
