# Standard PyPi packaging.
# Build materials and push to pypi.org.
# Author: Scott Woods <scott.suzuki@gmail.com>
import sys
import setuptools
import re

#
#
VERSION_PATTERN = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)')

#
#
with open("PACKAGE", "r", encoding="utf-8") as f:
	p = f.read()
PACKAGE = p[:-1]

#
#
with open("DESCRIPTION", "r", encoding="utf-8") as f:
	d = f.read()
DESCRIPTION = d[:-1]

#
#
with open("VERSION", "r", encoding="utf-8") as f:
	line = [t for t in f]
VERSION = line[-1][:-1]

if not VERSION_PATTERN.match(VERSION):
	print('Version "%s" does not meet semantic requirements' % (VERSION,))
	sys.exit(1)

with open("README.md", "r", encoding="utf-8") as f:
	long_description = f.read()

with open("DOC_LATEST_LINK", "r", encoding="utf-8") as f:
	d = f.read()
DOC_LINK = d[:-1]

REQUIRES = [
	"defusedxml>=0.7.1",
	"python-dateutil>=2.8.1",
]

setuptools.setup(
	name=PACKAGE,
	version=VERSION,
	author="Scott Woods",
	author_email="scott.suzuki@gmail.com",
	description=DESCRIPTION,
	long_description=long_description,
	long_description_content_type="text/markdown",
	# url="https://gitlab.com/scott.ansar/ansar-encode",
	project_urls={
		"Documentation": DOC_LINK,
	},
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Libraries",
	],
	# Where multiple packages might be found, esp if using standard
	# layout for "find_packages".
	package_dir={
		"": "src",
	},
	# First folder under "where" defines the name of the
	# namespace. Folders under that (with __init__.py files)
	# define import packages under that namespace.
	packages=setuptools.find_namespace_packages(
		where="src",
	),
	entry_points = {
		'console_scripts': [
			'ansar-releasing=ansar.command.show_release:main',
		],
	},
	python_requires=">=3.6",
	install_requires=REQUIRES,
)
