# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proto', 'proto.message']

package_data = \
{'': ['*']}

install_requires = \
['PySocks>=1.7.1,<2.0.0',
 'base58>=2.1.1,<3.0.0',
 'bitstring>=3.1.9,<4.0.0',
 'coincurve>=17.0.0,<18.0.0',
 'cryptography>=36.0.1,<37.0.0']

setup_kwargs = {
    'name': 'pyln-proto',
    'version': '23.5',
    'description': 'This package implements some of the Lightning Network protocol in pure python. It is intended for protocol testing and some minor tooling only. It is not deemed secure enough to handle any amount of real funds (you have been warned!).',
    'long_description': '# pyln-proto: Lightning Network protocol implementation\n\nThis package implements some of the Lightning Network protocol in pure\npython. It is intended for protocol testing and some minor tooling only. It is\nnot deemed secure enough to handle any amount of real funds (you have been\nwarned!).\n\n\n## Installation\n\n`pyln-proto` is available on `pip`:\n\n```\npip install pyln-proto\n```\n\nAlternatively you can also install the development version to get access to\ncurrently unreleased features by checking out the Core Lightning source code and\ninstalling into your python3 environment:\n\n```bash\ngit clone https://github.com/ElementsProject/lightning.git\ncd lightning/contrib/pyln-proto\npoetry install\n```\n\nThis will add links to the library into your environment so changing the\nchecked out source code will also result in the environment picking up these\nchanges. Notice however that unreleased versions may change API without\nwarning, so test thoroughly with the released version.\n',
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
