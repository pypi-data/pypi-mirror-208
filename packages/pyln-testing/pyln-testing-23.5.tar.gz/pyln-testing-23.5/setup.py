# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['testing']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.3,<3.0.0',
 'cheroot>=8.6.0,<9.0.0',
 'ephemeral-port-reserve>=1.1.4,<2.0.0',
 'grpcio>=1.47',
 'jsonschema>=4.4.0,<5.0.0',
 'protobuf>=3.20.3,<4',
 'psutil>=5.9.0,<6.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'pyln-client>=0.12.1',
 'pytest>=7.0.1,<8.0.0',
 'python-bitcoinlib>=0.11.0,<0.12.0']

setup_kwargs = {
    'name': 'pyln-testing',
    'version': '23.5',
    'description': 'Test your Core Lightning integration, plugins or whatever you want',
    'long_description': '# pyln-testing: A library to write tests against Core Lightning\n\nThis library implements a number of utilities that help building tests for\nCore Lightning nodes. In particular it provides a number of pytest fixtures that\nallow the management of a test network of a given topology and then execute a\ntest scenarion.\n\n`pyln-testing` is used by Core Lightning for its internal tests, and by the\ncommunity plugin directory to exercise the plugins.\n\n## Installation\n\n`pyln-testing` is available on `pip`:\n\n```bash\npip install pyln-testing\n```\n\nAlternatively you can also install the development version to get access to\ncurrently unreleased features by checking out the Core Lightning source code and\ninstalling into your python3 environment:\n\n```bash\ngit clone https://github.com/ElementsProject/lightning.git\ncd lightning/contrib/pyln-testing\npoetry install\n```\n\nThis will add links to the library into your environment so changing the\nchecked out source code will also result in the environment picking up these\nchanges. Notice however that unreleased versions may change API without\nwarning, so test thoroughly with the released version.\n\n',
    'author': 'Christian Decker',
    'author_email': 'decker.christian@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
