from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in trello/__init__.py
from trello import __version__ as version

setup(
	name="trello",
	version=version,
	description="trello",
	author="korecent solutions pvt. ltd",
	author_email="kamal@korecent.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
