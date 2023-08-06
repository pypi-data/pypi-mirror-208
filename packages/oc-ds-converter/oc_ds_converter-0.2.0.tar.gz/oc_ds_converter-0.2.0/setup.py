# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oc_ds_converter',
 'oc_ds_converter.crossref',
 'oc_ds_converter.datacite',
 'oc_ds_converter.datasource',
 'oc_ds_converter.jalc',
 'oc_ds_converter.lib',
 'oc_ds_converter.medra',
 'oc_ds_converter.oc_idmanager',
 'oc_ds_converter.preprocessing',
 'oc_ds_converter.pubmed',
 'oc_ds_converter.run']

package_data = \
{'': ['*'], 'oc_ds_converter.pubmed': ['support_files/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'beautifulsoup4>=4.12.1,<5.0.0',
 'fakeredis>=2.12.1,<3.0.0',
 'lxml>=4.9.2,<5.0.0',
 'ndjson>=0.3.1,<0.4.0',
 'pandas>=2.0.1,<3.0.0',
 'pebble>=5.0.3,<6.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'redis>=4.5.5,<5.0.0',
 'requests>=2.28.2,<3.0.0',
 'tqdm>=4.65.0,<5.0.0',
 'validators>=0.20.0,<0.21.0',
 'xmltodict>=0.13.0,<0.14.0',
 'zstandard>=0.21.0,<0.22.0']

setup_kwargs = {
    'name': 'oc-ds-converter',
    'version': '0.2.0',
    'description': 'A library for converting metadata provided by various data sources, e.g. Crossref, DataCite, JaLC, and mEDRA, into the format used by OpenCitations Meta.',
    'long_description': '[<img src="https://img.shields.io/badge/powered%20by-OpenCitations-%239931FC?labelColor=2D22DE" />](http://opencitations.net)\n[![Run tests](https://github.com/opencitations/ra_processor/actions/workflows/run_tests.yml/badge.svg)](https://github.com/opencitations/oc_meta/actions/workflows/run_tests.yml)\n![Coverage](https://raw.githubusercontent.com/opencitations/ra_processor/main/test/coverage/coverage.svg)\n<!-- ![PyPI](https://img.shields.io/pypi/pyversions/oc_meta) -->\n![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/opencitations/ra_processor)\n\n\n\n# OpenCitations Data Sources Converter\n\nThis repository contains scripts useful for converting scholarly bibliographic metadata from various data sources into the format accepted by OpenCitations Meta. The data sources currently supported are Crossref, DataCite, PubMed, mEDRA a JaLC.\n',
    'author': 'arcangelo7',
    'author_email': 'arcangelomas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
