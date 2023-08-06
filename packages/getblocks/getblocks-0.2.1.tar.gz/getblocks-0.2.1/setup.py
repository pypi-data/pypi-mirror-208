from setuptools import setup

from getblocks import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = "getblocks",
    version = __version__,
    description = "Down to the sector detail!",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/jblukach/getblocks",
    author = "John Lukach",
    author_email = "hello@lukach.io",
    license = "Apache-2.0",
    packages = [
        "getblocks"
    ],
    install_requires = [
        "aiofile",
        "blake3",
        "requests==2.29.0"
    ],
    zip_safe = False,
    entry_points = {
        "console_scripts": [
            "getblocks=getblocks.cli:main"
        ],
    },
    python_requires = ">=3.7",
)