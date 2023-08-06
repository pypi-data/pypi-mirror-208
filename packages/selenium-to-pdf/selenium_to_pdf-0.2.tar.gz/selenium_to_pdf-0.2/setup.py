# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['selenium_to_pdf']

package_data = \
{'': ['*']}

install_requires = \
['selenium>=4.9.1,<5.0.0']

setup_kwargs = {
    'name': 'selenium-to-pdf',
    'version': '0.2',
    'description': 'A simple utility to convert a web page to PDF using Selenium and Chrome.',
    'long_description': "# selenium-to-pdf\n\nGiven an HTML document, converts thereupon to a PDF using Selenium's DevTools.\n",
    'author': 'Mike Babb',
    'author_email': 'mike7400@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mkbabb/selenium-to-pdf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
