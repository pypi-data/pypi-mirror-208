# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['itasca',
 'itasca.ball',
 'itasca.ball.thermal',
 'itasca.ballarray',
 'itasca.ballballarray',
 'itasca.ballfacetarray',
 'itasca.ballpebblearray',
 'itasca.ballrblockarray',
 'itasca.clump',
 'itasca.clump.pebble',
 'itasca.clump.template',
 'itasca.clump.thermal',
 'itasca.clump.thermal.pebble',
 'itasca.clumparray',
 'itasca.contact',
 'itasca.dfn',
 'itasca.dfn.fracture',
 'itasca.dfn.inter',
 'itasca.dfn.setinter',
 'itasca.dfn.template',
 'itasca.dfn.vertex',
 'itasca.facetarray',
 'itasca.fish',
 'itasca.measure',
 'itasca.pebblearray',
 'itasca.pebblefacetarray',
 'itasca.pebblepebblearray',
 'itasca.pebblerblockarray',
 'itasca.rblock',
 'itasca.rblock.template',
 'itasca.rblockarray',
 'itasca.rblockfacetarray',
 'itasca.rblockrblockarray',
 'itasca.vertexarray',
 'itasca.wall',
 'itasca.wall.facet',
 'itasca.wall.thermal',
 'itasca.wall.thermal.facet',
 'itasca.wall.vertex',
 'itasca.wallarray']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'itasca-stub',
    'version': '1.0.19',
    'description': 'Itasca PFC python stub',
    'long_description': "# itasca-stub\n\nThis repository contains code to generate `itasca.pyi` for PFC600.\n\nItasca provides great python interface, But it is too weak compared to PyCharm.\nWhen writing PFC in PyCharm, the keyword `itasca` has no typehint.\nThus, the project is developed, and here's a preview.\n\n![preview](https://raw.githubusercontent.com/panhaoyu/itasca-stub/master/doc/assets/preview.png)\n\n## Installation\n\n### Manual\n\nCopy the `itasca` directory to your python `site-packages` directory.\nMake sure to copy to your current environment.\nIf the internal Python of PFC is used, then you should copy to the path like:\n`Itasca\\PFC600\\exe64\\python36\\Lib\\site-packages`.\n\n### pip\n\n```cmd\npip install itasca-stub\n```\n\nBest wishes!\n\n## Contribution\n\nYou can submit issues and PRs at any time, welcome for your contribution!",
    'author': 'panhaoyu',
    'author_email': 'panhaoyu.china@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/panhaoyu/itasca-stub',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
