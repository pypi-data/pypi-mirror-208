#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'datapress', '__version__.py')) as f:
    exec(f.read(), about)

# load the README file and use it as the long_description for PyPI
with open('README.md', 'r') as f:
    readme = f.read()

# package configuration - for reference see:
# https://setuptools.readthedocs.io/en/latest/setuptools.html#id9
setup(
    name='datapress-client',
    description='DataPress API client',
    long_description=readme,
    long_description_content_type='text/markdown',
    version=about['__version__'],
    author='DataPress Ltd.',
    author_email='admin@datapress.com',
    url='https://github.com/datapressio/datapress-client',
    packages=['datapress'],
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        'pandas>=1.5',
        'requests',
        'xlrd',
        'openpyxl',
        'python-dotenv',
        'odfpy',
    ],
    license='Apache 2.0',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    keywords=''
)
