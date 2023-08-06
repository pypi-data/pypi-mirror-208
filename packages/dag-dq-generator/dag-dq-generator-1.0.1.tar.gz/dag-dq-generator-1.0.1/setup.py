import os
import sys
from setuptools import setup

# Package meta-data.
NAME = "dag-dq-generator"
PKG_NAME = "dag_dq_generator"
DESCRIPTION = "DPaaS Airflow DAG (Dynamic Acyclic Graph) and DQ (Data Quality) generator"
URL = "https://git.corp.adobe.com/ccea/dag-dq-generator"
EMAIL = "ccea-data-engineering@adobe.com"
AUTHOR = "CI DMe Data Engineering"
REQUIRES_PYTHON = ">=3.7.0"
VERSION = None

with open('requirements.txt') as f:
    requirements = f.readlines()

def readme():
    with open('README.md') as f:
        return f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
here = os.path.abspath(os.path.dirname(__file__))
if not VERSION:
    with open(os.path.join(here, PKG_NAME, "__version__.py")) as f:
        exec(f.read(), about)

setup(name=NAME,
      version=about["__version__"],
      description = DESCRIPTION,
      long_description = readme(),
      classifiers = [
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
      ],
      keywords = 'airflow dag data-quality',
      url = URL,
      author = AUTHOR,
      author_email = EMAIL,
      license = 'MIT',
      packages = [PKG_NAME],
      install_requires = requirements,
      entry_points = {
          'console_scripts': ['dag-generator=dag_dq_generator.dag_generator:main'],
      },
      include_package_data = True,
      zip_safe = False)
