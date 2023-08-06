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
    'version': '0.3.0',
    'description': "Given an HTML document, converts thereupon to a PDF using Selenium's DevTools.",
    'long_description': '# selenium-to-pdf\n\nGiven an HTML document, converts thereupon to a PDF using Selenium\'s DevTools.\n\nRequires selenium and ChromeDriver. For more information on how to install ChromeDriver,\nsee [here](https://sites.google.com/a/chromium.org/chromedriver/getting-started).\n\n## Example\n\n```python\nfrom selenium_to_pdf import convert\n\nurl = "https://www.fulltextarchive.com/book/dante-s-inferno/#CANTO-1-2"\n\npdf_data = convert.html_to_pdf(url=url)\n\nwith open("dante.pdf", "wb") as f:\n    f.write(pdf_data)\n```\n',
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
