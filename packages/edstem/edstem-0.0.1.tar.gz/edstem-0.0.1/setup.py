# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edstem', 'edstem.api']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.30.0,<3.0.0']

setup_kwargs = {
    'name': 'edstem',
    'version': '0.0.1',
    'description': 'A 3rd-party Python wrapper for the (unofficial) EdStem API. Not maintained by EdStem staff.',
    'long_description': '# EdStem - Python Wrapper\n\nA library of useful classes for interacting with the (unofficial) [EdStem](https://edstem.org) API.\n\n**Author**: Hunter Schafer (hunterschafer@gmail.com)\n\n* Note: The author of this library is not affiliated with EdStem.\n\nAny questions or comments can be handled here on GitHub or you can email me at [hunterschafer@gmail.com](mailto:hunterschafer@gmail.com).\n\n## Publish New Version\n\nSee [here](https://realpython.com/pypi-publish-python-package/#publish-your-package-to-pypi)\n\n',
    'author': 'Hunter Schafer',
    'author_email': 'hunterschafer@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
