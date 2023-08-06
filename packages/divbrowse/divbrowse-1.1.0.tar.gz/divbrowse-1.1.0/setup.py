# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['divbrowse', 'divbrowse.brapi', 'divbrowse.brapi.v2', 'divbrowse.lib']

package_data = \
{'': ['*'], 'divbrowse': ['static/*', 'static/build/*', 'tests/data/*']}

install_requires = \
['bioblend>=0.16.0,<0.17.0',
 'click>=8.0.1,<9.0.0',
 'flask>=2.0.1,<3.0.0',
 'numpy>=1.21.1,<2.0.0',
 'orjson>=3.8.5,<4.0.0',
 'pandas>=1.3.0,<2.0.0',
 'pyyaml>=5.4.1,<6.0.0',
 'scikit-allel>=1.3.5,<2.0.0',
 'scikit-learn>=1.2.0,<2.0.0',
 'seaborn>=0.12.2,<0.13.0',
 'simplejson>=3.17.3,<4.0.0',
 'tables>=3.6.1,<4.0.0',
 'umap-learn>=0.5.2,<0.6.0',
 'waitress==2.1.2',
 'zarr>=2.8.3,<3.0.0']

extras_require = \
{'docs': ['sphinx>=4.0.2,<5.0.0',
          'sphinx-autoapi>=1.6.0,<2.0.0',
          'sphinx_rtd_theme>=0.5.2,<0.6.0',
          'sphinx-click>=3.0.1,<4.0.0']}

entry_points = \
{'console_scripts': ['divbrowse = divbrowse.cli:main']}

setup_kwargs = {
    'name': 'divbrowse',
    'version': '1.1.0',
    'description': 'A web application for interactive visualization and analysis of genotypic variant matrices',
    'long_description': '<img src="docs/source/images/divbrowse_logo.png" width="600">\n<br />\n\n[![PyPI](https://img.shields.io/pypi/v/divbrowse?color=blue&label=PyPI.org)](https://pypi.org/project/divbrowse/)\n[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/ipkbit/divbrowse?color=blue&label=DockerHub)](https://hub.docker.com/r/ipkbit/divbrowse)\n![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/IPK-BIT/divbrowse?color=blue&label=Github)\n\n[![Preprint on bioRxiv.org](https://img.shields.io/badge/DOI-10.1101%2F2022.09.22.509016-yellow)](https://doi.org/10.1101/2022.09.22.509016)\n\n[![Documentation Status](https://readthedocs.org/projects/divbrowse/badge/?version=latest)](https://divbrowse.readthedocs.io/?badge=latest)\n[![Python](https://img.shields.io/pypi/pyversions/divbrowse.svg?color=green)](https://badge.fury.io/py/divbrowse)\n[![PyPI Downloads](https://img.shields.io/pypi/dm/divbrowse.svg?label=PyPI%20downloads)](https://pypi.org/project/divbrowse/)\n[![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/divbrowse)](https://libraries.io/pypi/divbrowse)\n![License](https://img.shields.io/github/license/IPK-BIT/divbrowse)\n\n<br />\n\n**Website:** https://divbrowse.ipk-gatersleben.de   \n**Documentation:** https://divbrowse.readthedocs.io\n\n<hr />\n\n**Table of contents:**\n  - [About DivBrowse](#about-divbrowse)\n  - [Try out DivBrowse](#try-out-divbrowse)\n  - [Screenshots](#screenshots)\n  - [Usage workflow concept](#usage-workflow-concept)\n  - [Architecture](#architecture)\n\n<br />\n\n## About DivBrowse\n\nDivBrowse is a web application for interactive exploration and analysis of very large SNP matrices.\n\nIt offers a novel approach for interactive visualization and analysis of genomic diversity data and optionally also gene annotation data. The use of standard file formats for data input supports interoperability and seamless deployment of application instances based on established bioinformatics pipelines. The possible integration into 3rd-party web applications supports interoperability and reusability.\n\nThe integrated ad-hoc calculation of variant summary statistics and principal component analysis enables the user to perform interactive analysis of population structure for single genetic features like genes, exons and promoter regions. Data interoperability is achieved by the possibility to export genomic diversity data for genomic regions of interest in standardized VCF files.\n\n\n## Try out DivBrowse\n\nIf you want to test DivBrowse please visit the demo instances listed here:\nhttps://divbrowse.ipk-gatersleben.de/#demo-instances\n\n\n## Screenshots\n\n![DivBrowse GUI](https://github.com/IPK-BIT/divbrowse/blob/main/docs/source/images/divbrowse_main_gui_screenshot.png?raw=true)\n\n\n## Usage workflow concept\n\n![Usage workflow concept](https://github.com/IPK-BIT/divbrowse/blob/main/docs/source/images/paper_figures_usage_concept.png?raw=true)\n\n\n## Architecture\n\n![Architecture](https://github.com/IPK-BIT/divbrowse/blob/main/docs/source/images/paper_figures_general_architecture.png?raw=true)',
    'author': 'Patrick König',
    'author_email': 'koenig@ipk-gatersleben.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://divbrowse.ipk-gatersleben.de/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
