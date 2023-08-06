#!/usr/bin/env python3

"""Setup and install chainedci."""

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def readme():
    """Set Readme from file."""
    with open('README.md', encoding="utf-8") as f:
        return f.read()


setup(name='chainedci',
      version='1.5.28',
      description='Chaine Gitlab CI pipelines',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://gitlab.com/Orange-OpenSource/lfn/ci_cd/chained-ci',
      author='Orange OpenSource',
      license='Apache 2.0',
      packages=find_packages(),
      py_modules=[splitext(basename(path))[0] for path in glob('*.py')],
      include_package_data=True,
      scripts=["chainedci/chainedci"],
      install_requires=[
          "ansible-core==2.15.0",
          "GitPython==3.1.31",
          "Jinja2==3.1.2",
          "requests==2.30.0",
          "schema==0.7.5",
          "urllib3 ==2.0.2"
      ],
      setup_requires=["pytest-runner"],
      tests_require=[
          "pytest",
          "pytest-cov",
          "pytest-mock",
          "mock",
          "requests_mock"
      ],
      zip_safe=False)
