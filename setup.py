#!/usr/bin/python3

try:
    from rjgtoys.projects import setup
except ImportError:
    from setuptools import setup

setup(
    name = "rjgtoys-tkthread",
    version = "0.0.1",
    author = "Bob Gautier",
    author_email = "bob.gautier@gmail.com",
    description = ("Enable use of threads with tkinter"),
    keywords = "tk tkinter thread",
    namespace_packages=['rjgtoys'],
    packages = ['rjgtoys','rjgtoys.tkthread'],
)
