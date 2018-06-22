# -*- coding: utf-8 -*-

import os

# Enable UTF support in both Python 2 and 3: https://stackoverflow.com/a/10975371/1883424
from io import open
from setuptools import setup, find_packages

script_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(script_dir, "README.rst"), encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="django_resetdb",
    version="0.2.2",
    description="Management command to reset your Django database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/GreenBankObservatory/django-resetdb",
    author="Thomas Chamberlin",
    author_email="tchamber@nrao.edu",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # 'Topic :: Software Development :: Build Tools',
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
