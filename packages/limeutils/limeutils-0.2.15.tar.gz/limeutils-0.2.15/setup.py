# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['limeutils', 'limeutils.redis']

package_data = \
{'': ['*']}

install_requires = \
['hiredis>=2.2.3,<3.0.0',
 'pydantic>=1.10.7,<2.0.0',
 'pytz>=2023.3,<2024.0',
 'redis>=4.5.5,<5.0.0']

setup_kwargs = {
    'name': 'limeutils',
    'version': '0.2.15',
    'description': '',
    'long_description': "limeutils\n============\n\nLimeutils is a small collection of classes and methods for dealing with Redis data and a few other helpful functions. Check out the documentation for information\n. More classes to be added as needed.\n\nThis package uses [Pydantic models][pydantic] to validate its data.\n\n[pydantic]: https://pydantic-docs.helpmanual.io/ 'Pydantic'\n\n\nInstallation\n--------------\n\n### Install with poetry\n\n```bash\npoetry add limeutils\n```\n\n### Install by repo\n\n```\npip install git+https://github.com/dropkickdev/limeutils.git@develop#egg=limeutils\n```\n\n### Install with `git clone`\n\nSimply install from the root folder\n\n```\n# This can also be a fork\ngit clone https://github.com/dropkickdev/limeutils.git\n\ncd limeutils\npoetry install\n```\n\n## Documentation\n\nView the documentation at: https://dropkickdev.github.io/limeutils/",
    'author': 'enchance',
    'author_email': 'enchance@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/dropkickdev/limeutils.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
