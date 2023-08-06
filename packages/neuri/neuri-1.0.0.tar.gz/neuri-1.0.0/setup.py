import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def open_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))

setup(
  name = 'neuri',
  packages = ['neuri'],
  version = '1.0.0',
  license=open('LICENSE.txt').read(),
  description = 'Python client library for the Neuri API',
  author = 'Neuri',
  author_email = 'support@neuri.ai',
  url = 'https://github.com/Neuri-ai/python-client',  # use the URL to the github repo
  keywords = ["api client", "neuri", "neuri.ai", "neuri api"],
  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Operating System :: OS Independent'
  ],
  long_description=open_file('README.rst').read(),
  long_description_content_type="text/markdown",
  install_requires=[
    'requests'
  ],
  python_requires='>=3.7'
)