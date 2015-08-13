#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.test import test as _test


class test(_test):
    def finalize_options(self):
        _test.finalize_options(self)
        self.test_args.insert(0, 'discover')


setup(
    name="insteonrf",
    version="1.0",
    packages=find_packages(),
    # install_requires=[
    #     "libusb1",
    # ],
    test_suite='insteonrf.test',
    author="Peter Shipley",
    author_email="evilpete@gmail.com",
    description="",
    license="",
    keywords="insteon insteonrf radio home_automation",
    url="",
)
