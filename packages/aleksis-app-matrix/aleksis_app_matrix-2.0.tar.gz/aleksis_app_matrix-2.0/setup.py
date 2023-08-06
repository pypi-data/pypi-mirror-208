# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.matrix',
 'aleksis.apps.matrix.migrations',
 'aleksis.apps.matrix.tests',
 'aleksis.apps.matrix.util']

package_data = \
{'': ['*'],
 'aleksis.apps.matrix': ['frontend/*',
                         'frontend/messages/*',
                         'locale/*',
                         'locale/ar/LC_MESSAGES/*',
                         'locale/de_DE/LC_MESSAGES/*',
                         'locale/fr/LC_MESSAGES/*',
                         'locale/la/LC_MESSAGES/*',
                         'locale/nb_NO/LC_MESSAGES/*',
                         'locale/ru/LC_MESSAGES/*',
                         'locale/tr_TR/LC_MESSAGES/*',
                         'locale/uk/LC_MESSAGES/*',
                         'templates/matrix/room/*'],
 'aleksis.apps.matrix.tests': ['synapse/*']}

install_requires = \
['aleksis-core>=3.0,<4.0']

entry_points = \
{'aleksis.app': ['matrix = aleksis.apps.matrix.apps:DefaultConfig']}

setup_kwargs = {
    'name': 'aleksis-app-matrix',
    'version': '2.0',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp Matrix (Integration with Matrix/Element)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp Matrix (Integration with Matrix/Element)\n==================================================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\nThe author of this app did not describe it yet.\n\nLicence\n-------\n\n::\n\n  Copyright © 2021, 2022 Jonathan Weth <dev@jonathanweth.de>\n\n  Licenced under the EUPL, version 1.2 or later\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\n.. _AlekSIS®: https://edugit.org/AlekSIS/AlekSIS\n.. _European Union Public Licence: https://eupl.eu/\n',
    'author': 'Jonathan Weth',
    'author_email': 'dev@jonathanweth.de',
    'maintainer': 'Jonathan Weth',
    'maintainer_email': 'wethjo@katharineum.de',
    'url': 'https://aleksis.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
