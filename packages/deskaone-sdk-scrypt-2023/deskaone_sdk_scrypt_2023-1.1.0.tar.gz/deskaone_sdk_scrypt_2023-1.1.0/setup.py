# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['deskaone_sdk_scrypt_2023',
 'deskaone_sdk_scrypt_2023.Client',
 'deskaone_sdk_scrypt_2023.Database',
 'deskaone_sdk_scrypt_2023.Exceptions',
 'deskaone_sdk_scrypt_2023.Internal',
 'deskaone_sdk_scrypt_2023.Utils',
 'deskaone_sdk_scrypt_2023.Utils.WebShare']

package_data = \
{'': ['*']}

install_requires = \
['base58>=2.1.1,<3.0.0',
 'bs4>=0.0.1,<0.0.2',
 'colorama>=0.4.6,<0.5.0',
 'flask>=2.2.3,<3.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'html5lib>=1.1,<2.0',
 'install-jdk>=0.3.0,<0.4.0',
 'polling2>=0.5.0,<0.6.0',
 'polling>=0.3.2,<0.4.0',
 'pycryptodome>=3.17,<4.0',
 'pysocks>=1.7.1,<2.0.0',
 'python-dotenv>=1.0.0,<2.0.0',
 'random-user-agent>=1.0.1,<2.0.0',
 'requests[socks]>=2.28.2,<3.0.0',
 'sqlalchemy==1.4.29']

setup_kwargs = {
    'name': 'deskaone-sdk-scrypt-2023',
    'version': '1.1.0',
    'description': '',
    'long_description': 'xxxxxxxxxxxxxxxx',
    'author': 'Antoni Oktha Fernandes',
    'author_email': '37358597+DesKaOne@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
