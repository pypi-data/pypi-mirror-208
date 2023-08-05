# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['odapqi',
 'odapqi.api',
 'odapqi.api.classes',
 'odapqi.display',
 'odapqi.display.components',
 'odapqi.display.components.export',
 'odapqi.display.components.overview',
 'odapqi.display.components.segment',
 'odapqi.display.components.tabs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'odap-qi',
    'version': '0.1.1',
    'description': 'ODAP Quick Insights',
    'long_description': '# ODAP Quick Insights\n',
    'author': 'Jan Petrik',
    'author_email': 'jan.petrik@datasentics.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/DataSentics/odap-qi',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
