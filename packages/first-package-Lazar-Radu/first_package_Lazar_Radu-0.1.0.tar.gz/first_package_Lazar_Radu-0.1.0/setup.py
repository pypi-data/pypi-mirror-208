from setuptools import setup

setup(
    name="first_package_Lazar_Radu",
    version="0.1.0",
    author="Lazar Radu",
    author_email="radubond@yahoo.com",
    packages=["my_own_package"],
    package_dir={"": "src"},
    include_package_data=True,
    description="My_first_package"
)
