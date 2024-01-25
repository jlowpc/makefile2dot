'''
Create the pypi package.
'''

from setuptools import setup

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name='makefile2dot',
    version='1.0.5',
    author='Chad Gilbert',
    author_email='chad.s.gilbert@gmail.com',
    description='Create a graphviz graph of a Makefile.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=["makefile2dot"],
    scripts=["scripts/makefile2dot"],
    install_requires=[
        'graphviz',
        ],
    url='https://github.com/chadsgilbert/makefile2dot',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX'
        ],
)
