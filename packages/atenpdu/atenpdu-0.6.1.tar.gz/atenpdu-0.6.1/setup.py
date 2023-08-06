# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['atenpdu', 'atenpdu.mibs']

package_data = \
{'': ['*']}

install_requires = \
['async-timeout>=4.0.2,<5.0.0', 'pysnmplib>=5.0.21,<6.0.0']

entry_points = \
{'console_scripts': ['pductl = atenpdu.pductl:run']}

setup_kwargs = {
    'name': 'atenpdu',
    'version': '0.6.1',
    'description': 'Interface for ATEN-PE PDUs',
    'long_description': '# pductl - Control outlets of ATEN PE PDUs\n\n## Installation\n\n```sh\npip install atenpdu\n```\n \n## Example configuration [~/.pductl]\n```json\n{\n  "format": 1,\n  "pdus": {\n    "pdu1": {\n      "node": "pdu1",\n      "service": "snmp",\n      "username": "administrator",\n      "authkey": "AAAAAAAAAAAAAA",\n      "privkey": "BBBBBBBBBBBBBB"\n    },\n    "pdu2": {\n      "authkey": "CCCCCCCCCCCCCC",\n      "privkey": "DDDDDDDDDDDDDD"\n    },\n    "pdu3": {\n      "node": "192.168.21.19",\n      "service": "16161",\n      "username": "joe",\n      "authkey": "EEEEEEEEEEEEEE",\n      "privkey": "FFFFFFFFFFFFFF"\n    },\n    "pdu4": {\n      "community": "private"\n    },\n    "pdu5": {\n    }\n  }\n}\n```\n\n* `authkey` and `privkey` are required for SNMPv3. On absence, SNMPv2c gets used.\n* `community` defaults to `private` for SNMPv2c.\n* `node` defaults to PDU entry\'s name.\n* `service` defaults to `snmp`, i.e. port 161.\n* `username` defaults to `administrator` for SNMPv3.\n\n## Usage\n\n```sh\npductl [-p <PDU>] list\npductl [-p <PDU>] <on|off|reboot|status> <OUTLET> [<OUTLET> ...]\n```\n\nUse `ALL` to select all outlets.\n',
    'author': 'Andreas Oberritter',
    'author_email': 'obi@saftware.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mtdcr/pductl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)
