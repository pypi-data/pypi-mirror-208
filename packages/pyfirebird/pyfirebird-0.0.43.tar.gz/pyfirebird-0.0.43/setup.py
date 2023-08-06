import os
from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.dirname(os.path.abspath(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md"), "r") as f:
    README = f.read()

# This call to setup() does all the work
setup(
    name="pyfirebird",
    version="0.0.43",
    description="Streaming Data Processing Framework",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/stonezhong/firebird",
    author="Stone Zhong",
    author_email="stonezhong@hotmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    package_dir = {'': 'src'},
    packages=find_packages(where='src'),
    package_data={"firebirdconsole": ["ui/templates/*", "ui/static/js-bundle/*", "ui/static/images/*"]},
    include_package_data=True,
    install_requires=["pika", "kazoo", "docker", "paramiko", "Django>=4.2.1", "mysqlclient", "graphviz>=0.20.1"],
    entry_points={
        "console_scripts": [
            "pipeline=firebird.cmd_tools.pipeline:main",
            "executor=firebird.cmd_tools.executor:main",
            "fbconsole=firebird.cmd_tools.fbconsole:main",
        ]
    },
)

