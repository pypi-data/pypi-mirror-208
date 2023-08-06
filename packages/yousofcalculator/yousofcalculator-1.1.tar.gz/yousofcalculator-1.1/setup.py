import setuptools
from pathlib import Path

setuptools.setup(
    name="yousofcalculator",
    version=1.1,
    author="Yousof",
    author_email="ysufali9999@gmail.com",
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests","data"])
)