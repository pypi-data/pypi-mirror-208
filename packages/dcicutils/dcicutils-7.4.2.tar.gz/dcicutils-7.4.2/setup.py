# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.', 'scripts': 'dcicutils/scripts'}

packages = \
['dcicutils', 'dcicutils.scripts', 'scripts']

package_data = \
{'': ['*'], 'dcicutils': ['kibana/*']}

install_requires = \
['PyJWT>=2.6.0,<3.0.0',
 'PyYAML>=5.1,<5.5',
 'aws-requests-auth>=0.4.2,<1',
 'boto3>=1.17.39,<2.0.0',
 'botocore>=1.20.39,<2.0.0',
 'docker>=4.4.4,<5.0.0',
 'elasticsearch==7.13.4',
 'gitpython>=3.1.2,<4.0.0',
 'opensearch-py>=2.0.1,<3.0.0',
 'pyOpenSSL>=23.1.1,<24.0.0',
 'pytz>=2020.4',
 'redis>=4.5.1,<5.0.0',
 'requests>=2.21.0,<3.0.0',
 'rfc3986>=1.4.0,<2.0.0',
 'structlog>=19.2.0,<20.0.0',
 'toml>=0.10.1,<1',
 'tqdm>=4.65.0,<5.0.0',
 'typing-extensions>=3.8',
 'urllib3>=1.26.6,<2.0.0',
 'webtest>=2.0.34,<3.0.0']

entry_points = \
{'console_scripts': ['publish-to-pypi = '
                     'dcicutils.scripts.publish_to_pypi:main']}

setup_kwargs = {
    'name': 'dcicutils',
    'version': '7.4.2',
    'description': 'Utility package for interacting with the 4DN Data Portal and other 4DN resources',
    'long_description': '=====\nutils\n=====\n\nCheck out our full documentation `here <https://dcic-utils.readthedocs.io/en/latest/>`_\n\nThis repository contains various utility modules shared amongst several projects in the 4DN-DCIC. It is meant to be used internally by the DCIC team and externally as a Python API to `Fourfront <https://data.4dnucleome.org>`_\\ , the 4DN data portal.\n\npip installable as the ``dcicutils`` package with: ``pip install dcicutils``\n\nSee `this document <https://dcic-utils.readthedocs.io/en/latest/getting_started.html>`_ for tips on getting started. `Go here <https://dcic-utils.readthedocs.io/en/latest/examples.html>`_ for examples of some of the most useful functions.\n\n\n.. image:: https://travis-ci.org/4dn-dcic/utils.svg?branch=master\n   :target: https://travis-ci.org/4dn-dcic/utils\n   :alt: Build Status\n\n\n.. image:: https://coveralls.io/repos/github/4dn-dcic/utils/badge.svg?branch=master\n   :target: https://coveralls.io/github/4dn-dcic/utils?branch=master\n   :alt: Coverage\n\n.. image:: https://readthedocs.org/projects/dcic-utils/badge/?version=latest\n   :target: https://dcic-utils.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n',
    'author': '4DN-DCIC Team',
    'author_email': 'support@4dnucleome.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/4dn-dcic/utils',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
