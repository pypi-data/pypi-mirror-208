from setuptools import find_packages
from distutils.core import setup

long_description = open('README.md').read()

setup(
  name='orkg',
  packages=find_packages(),
  version='0.15.3',
  license='MIT',
  description='Python client for the Open Research Knowledge Graph (ORKG) API',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Yaser Jaradeh',
  author_email='jaradeh@l3s.de',
  url='http://orkg.org/about',
  download_url='https://gitlab.com/TIBHannover/orkg/orkg-pypi/-/archive/0.15.3/orkg-pypi-0.15.3.tar.gz',
  keywords=['ORKG', 'Scholarly communication', 'API wrapper'],
  install_requires=[
          'hammock',
          'pandas',
          'tqdm',
          'nose',
          'networkx',
          'cardinality',
          'Inflector'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8"
  ],
  test_suite='nose.collector',
  tests_require=['nose'],
)
