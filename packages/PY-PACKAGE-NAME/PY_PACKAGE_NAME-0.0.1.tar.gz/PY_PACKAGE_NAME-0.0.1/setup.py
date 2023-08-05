from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='PY_PACKAGE_NAME',
    license="MIT License",
    version='0.0.1',
    author='AUTHOR_NAME',
    author_email='AUTHOR_EMAIL@gmail.com',
    description='SHORT_DESCRIPTION',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/AUTHOR_NAME/YOUR_PACKAGE_NAME',
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        'requests',
    ],
    extras_require={
        "dev": [
            "pytest",
            "coverage",
            "mypy",
            "ruff",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "PY_PACKAGE_NAME=PY_PACKAGE_NAME.main:main",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
