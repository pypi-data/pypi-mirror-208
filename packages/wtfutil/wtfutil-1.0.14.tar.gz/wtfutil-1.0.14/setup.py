#!/usr/bin/env python

"""
"""

from setuptools import setup, Command
import io
import os
import sys
from codecs import open
from shutil import rmtree

__author__ = 'vicrack'
__version__ = '1.0.14'
__contact__ = '18179821+ViCrack@users.noreply.github.com'
__url__ = 'https://github.com/vicrack'
__license__ = 'BSD'
requires = [
    'pymysql',
    'faker',
    'requests',
    'cacheout',
    'requests_cache',
    'tldextract',
    'dns',
]

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


class PublishCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except FileNotFoundError:
            pass

        self.status('Building Source and Wheel (universal) distribution...')
        os.system('{} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine...')
        os.system('twine upload dist/*')

        sys.exit()


setup(name='wtfutil',
      version=__version__,
      description="A Python utility.",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author=__author__,
      author_email=__contact__,
      url=__url__,
      packages=['wtfutil'],
      include_package_data=True,
      zip_safe=False,
      license_file=__license__,
      install_requires=requires,
      platforms='any',
      classifiers=[
          # See: https://pypi.python.org/pypi?:action=list_classifiers
          'Topic :: Utilities',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Software Development :: Libraries',
          'Development Status :: 5 - Production/Stable',
          'Operating System :: OS Independent',
          # List of python versions and their support status:
          # https://en.wikipedia.org/wiki/CPython#Version_history
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
      ],
      cmdclass={
          'publish': PublishCommand,
      }
      )

"""
A brief checklist for release:

* tox
* git commit (if applicable)
* Bump setup.py version off of -dev
* git commit -a -m "bump version for x.y.z release"
* python setup.py sdist bdist_wheel upload
* bump docs/conf.py version
* git commit
* git tag -a x.y.z -m "brief summary"
* write CHANGELOG
* git commit
* bump setup.py version onto n+1 dev
* git commit
* git push

"""
