from setuptools import setup

setup(
    name="first-package-Razvan",
    version="0.1.0",
    author="Razvan",
    author_email="razvanstroe3st@gmail.com",
    packages=["my_own_package"],
    package_dir={"": "src"},
    include_package_data=True,
    description="My first package"
)
