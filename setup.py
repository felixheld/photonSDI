#!/usr/bin/env python3

import sys
from setuptools import setup
from setuptools import find_packages


if sys.version_info[:3] < (3, 3):
	raise SystemExit("You need Python 3.3+")


setup(
	name="photonsdi",
	version="0.0",
	description="small footprint and configurable SDI core",
	long_description=open("README").read(),
	author="Felix Held",
	author_email="felix@felixheld.de",
	url="https://github.com/felixheld/photonsdi",
	download_url="https://github.com/felixheld/photonsdi",
	license="BSD",
	platforms=["Any"],
	keywords="HDL ASIC FPGA hardware design",
	classifiers=[
		"Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
		"Environment :: Console",
		"Development Status :: Alpha",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: BSD License",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
	],
	packages=find_packages(),
	include_package_data=True,
)
