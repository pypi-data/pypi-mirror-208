import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

setup(
    name="wozoxutils",
    version="0.2.5",
    packages=find_packages(),
    install_requires=[
        'pyyaml>=6.0',
    ],
    author="illiten",
    author_email="admin@leelib.com",
    description="general-purpose library for Python that contains various commonly used functional modules",
    url="https://github.com/wozox/wozoxutils-py",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='wozox utils',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
