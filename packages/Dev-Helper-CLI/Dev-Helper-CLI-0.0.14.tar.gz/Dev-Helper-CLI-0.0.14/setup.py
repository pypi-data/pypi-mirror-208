import setuptools
import os

cwd = os.getcwd()

with open("README.md", "r", encoding="utf-8") as fhand:
    long_description = fhand.read()

setuptools.setup(
    name="Dev-Helper-CLI",
    version="0.0.14",
    author="Luis Moreno",
    author_email="luis.cfh.90@gmail.com",
    description=("A CLI program to help devs be more productive."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luigicfh/Dev-Helper-2.0",
    project_urls={
        "Bug Tracker": "https://github.com/luigicfh/Dev-Helper-2.0/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["PyYAML"],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "dh = dh.cli:parse",
        ]
    }
)