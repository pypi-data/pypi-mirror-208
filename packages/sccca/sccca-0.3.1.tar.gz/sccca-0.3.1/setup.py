# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scCCA', 'scCCA.plots', 'scCCA.train', 'scCCA.utils']

package_data = \
{'': ['*']}

install_requires = \
['adjusttext>=0.7.3,<0.8.0', 'pyro-ppl>=1.8.0', 'scanpy>=1.8.2']

extras_require = \
{'docs': ['Sphinx==4.2.0',
          'sphinx-rtd-theme==1.0.0',
          'sphinxcontrib-napoleon==0.7',
          'nbsphinx==0.8.9'],
 'notebook': ['jupyter']}

setup_kwargs = {
    'name': 'sccca',
    'version': '0.3.1',
    'description': 'Single cell canonical correlation analysis.',
    'long_description': 'None',
    'author': 'Harald Vohringer',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8.1,<3.11',
}


setup(**setup_kwargs)
