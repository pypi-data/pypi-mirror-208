# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['encord_active_components', 'encord_active_components.components']

package_data = \
{'': ['*'],
 'encord_active_components': ['frontend/*',
                              'frontend/assets/*',
                              'frontend/dist/*',
                              'frontend/dist/assets/*']}

install_requires = \
['streamlit>=1.19.0,<2.0.0']

setup_kwargs = {
    'name': 'encord-active-components',
    'version': '0.0.13',
    'description': 'Frontend components used by Encord Active',
    'long_description': 'None',
    'author': 'Cord Technologies Limited',
    'author_email': 'hello@encord.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*, !=3.8.*',
}


setup(**setup_kwargs)
