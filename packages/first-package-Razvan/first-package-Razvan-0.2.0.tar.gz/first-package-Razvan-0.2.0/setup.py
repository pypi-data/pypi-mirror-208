from setuptools import setup
from pathlib import Path

d = Path(__file__).parent
description = (d / "README.md").read_text()

setup(
    name="first-package-Razvan",
    version="0.2.0",
    author="Razvan",
    author_email="razvanstroe3st@gmail.com",
    packages=["my_own_package"],
    package_dir={"": "src"},
    include_package_data=True,
    description="My first package",
    long_description=description,
    long_description_content_type="text/markdown"
)
