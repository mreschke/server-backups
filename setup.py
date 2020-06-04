from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mreschke-serverbackups",
    version="1.0.0",
    description="Config driven server backups that feel like a simple backup.py script",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Matthew Reschke",
    author_email="mail@mreschke.com",
    license="MIT",
    url="http://github.com/mreschke/server-backups",

    # I am using Native namespaces see https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages
    packages=["mreschke.serverbackups"],
    zip_safe=False,
    python_requires=">=3.5",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Environment :: CLI Environment",
    ],
    install_requires=[
        "click==7.1.*",
        "colored==1.4.*",
        "prettyprinter==0.18.*",
        "pyyaml==5.3.*",
    ],
    entry_points={
        "console_scripts": [
            "serverbackups=mreschke.serverbackups.init:cli"
        ],
    },
)
