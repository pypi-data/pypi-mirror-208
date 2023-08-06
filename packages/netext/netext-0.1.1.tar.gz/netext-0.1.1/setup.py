# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netext',
 'netext.edge_rendering',
 'netext.edge_routing',
 'netext.geometry',
 'netext.layout_engines',
 'netext.rendering',
 'netext.shapes']

package_data = \
{'': ['*']}

install_requires = \
['bitarray>=2.6.2,<3.0.0',
 'cachetools>=5.3.0,<6.0.0',
 'grandalf>=0.7,<0.8',
 'mkdocstrings[python]>=0.20.0,<0.21.0',
 'networkx-stubs>=0.0.1,<0.0.2',
 'networkx[default]>=3.0,<4.0',
 'rich>=13,<14',
 'rtree>=1.0.1,<2.0.0',
 'shapely>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'netext',
    'version': '0.1.1',
    'description': 'A graph (network) rendering library for the terminal.',
    'long_description': '# netext\n\n[![pypi](https://img.shields.io/pypi/v/netext.svg)](https://pypi.python.org/pypi/netext)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)\n[![Documentation](https://img.shields.io/badge/documentation-latest-green)](https://mahrz24.github.io/netext/)\n\n![](logo.jpg)\n\nNetext is a graph (network) rendering library for the terminal. It uses the awesome [rich](https://rich.readthedocs.io/en/stable/introduction.html) library to format output and can use different layout engines to place nodes and edges. The library has a very simple API that allows to render graphs created with networkx and integrates well with applications that use rich to output to the terminal. All styling and formatting is done via attributes the nodes and edges of the networkx graph data structures using special attributes keys.\n\n![](example.svg)\n\nThe library is in its early stages and has currently no emphasis on performance, so please do not try to render large graphs with it. While it has been released expect some breaking API changes in the future. Node layout is currently provided by the [grandalf](https://github.com/bdcht/grandalf) library.\n',
    'author': 'Malte Klemm',
    'author_email': 'me@malteklemm.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mahrz24/netext',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
