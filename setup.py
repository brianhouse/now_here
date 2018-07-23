#!/usr/bin/env python3

from setuptools import setup

setup(
    name="now_here",
    version="0.1.0",
    description="Simple browser-based note-taking.",
    author="Brian House",
    author_email="brian.house@gmail.com",
    license='GPL3',
    packages=['now_here'],
    data_files=[('now_here', ['launch.sh', 'README.md', 'nginx.conf.smp', 'LICENSE.txt'])],
    install_requires=[
        "flask",
        "uwsgi",
        "pymongo",
        "diff-match-patch"
    ],
)
