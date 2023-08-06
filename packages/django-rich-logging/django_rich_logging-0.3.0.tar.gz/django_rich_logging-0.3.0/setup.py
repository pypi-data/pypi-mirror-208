# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_rich_logging']

package_data = \
{'': ['*']}

install_requires = \
['Django>3.0', 'rich>11.2.0']

extras_require = \
{'docs': ['Sphinx>=4.3.2,<5.0.0',
          'linkify-it-py>=1.0.3,<2.0.0',
          'myst-parser>=0.16.1,<0.17.0',
          'furo>=2021.11.23,<2022.0.0',
          'sphinx-copybutton>=0.4.0,<0.5.0',
          'sphinx-autobuild>=2021.3.14,<2022.0.0',
          'toml',
          'attrs>=21.4.0,<22.0.0']}

setup_kwargs = {
    'name': 'django-rich-logging',
    'version': '0.3.0',
    'description': 'A prettier way to see Django requests while developing.',
    'long_description': '<p align="center">\n  <a href="https://django-rich-logging.readthedocs.io"><h1 align="center">django-rich-logging</h1></a>\n</p>\n<p align="center">A prettier way to see Django requests while developing.</p>\n\n![PyPI](https://img.shields.io/pypi/v/django-rich-logging?color=blue&style=flat-square)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/django-rich-logging?color=blue&style=flat-square)\n![GitHub Sponsors](https://img.shields.io/github/sponsors/adamghill?color=blue&style=flat-square)\n\n📖 Complete documentation: https://django-rich-logging.readthedocs.io\n\n📦 Package located at https://pypi.org/project/django-rich-logging/\n\n## ⭐ Features\n\n- live-updating table of all requests while developing\n\n![demo of django-rich-logging](https://raw.githubusercontent.com/adamghill/django-rich-logging/main/django-rich-logging.gif)\n\n## Installation\n\n`poetry add django-rich-logging` OR `pip install django-rich-logging`\n\n### Configuration\n\n```python\n# settings.py\n\n# other settings here\n\nLOGGING = {\n    "version": 1,\n    "disable_existing_loggers": False,\n    "handlers": {\n        "django_rich_logging": {\n            "class": "django_rich_logging.logging.DjangoRequestHandler",\n            "level": "INFO",\n        },\n    },\n    "loggers": {\n        "django.server": {"handlers": ["django_rich_logging"], "level": "INFO"},\n        "django.request": {"level": "CRITICAL"},\n    },\n}\n\n# other settings here\n```\n\nRead all of the documentation at https://django-rich-logging.readthedocs.io.\n',
    'author': 'adamghill',
    'author_email': 'adam@adamghill.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/adamghill/django-rich-logging/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
