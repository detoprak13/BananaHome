#!/usr/bin/python

""" setup.py for mps.

https://np1.github.com/mps

"""

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup


setup(
    name="mps",
    version="0.20.16",
    description="Search, Stream and Download MP3",
    keywords=["MP3", "music", "audio", "search", "stream", "download"],
    author="nagev",
    long_description=open("README.rst").read(),
    author_email="np1nagev@gmail.com",
    url="http://github.com/np1/mps/",
    download_url="https://github.com/np1/mps/tarball/master",
    packages=['mps_pkg'],
    entry_points=dict(console_scripts=['mps = mps_pkg:main.main']),
    package_data={"": ["LICENSE", "README.rst", "CHANGELOG"]},
    classifiers=[
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Environment :: Console",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: MacOS :: MacOS 9",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: Microsoft :: Windows :: Windows XP",
        "Operating System :: Microsoft :: Windows :: Windows Vista",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
)
