from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open("jupylite_duckdb/_version.py", "r") as file:
    code = file.read()
    exec(code)
    _version = __version__  # type: ignore # noqa

setup(
    name="jupylite_duckdb",
    version=_version,  # type: ignore # noqa
    description="Testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iqmo-org/",
    author="iqmo",
    author_email="info@iqmo.com",
    classifiers=[],
    keywords="jupyterlite duckdb wasm",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=["pandas"],
)
