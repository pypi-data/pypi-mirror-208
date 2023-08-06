import re

from setuptools import find_packages, setup

install_requirements = ["attrs>=22.2.0", "cleancat", "python-dateutil"]

VERSION_FILE = "cleanchausie/__init__.py"
with open(VERSION_FILE, encoding="utf8") as fd:
    version = re.search(r'__version__ = ([\'"])(.*?)\1', fd.read()).group(2)

README_FILE = "README.md"
with open(README_FILE, encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name="cleanchausie",
    version=version,
    url="http://github.com/closeio/cleanchausie",
    license="MIT",
    author="Alec Rosenbaum",
    author_email="engineering@close.io",
    maintainer="Alec Rosenbaum",
    maintainer_email="engineering@close.io",
    description="Data validation and transformation library for Python. Successor to CleanCat.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["cleanchausie", "cleanchausie.*"]),
    package_data={"cleanchausie": ["py.typed"]},
    zip_safe=False,
    platforms="any",
    install_requires=install_requirements,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
