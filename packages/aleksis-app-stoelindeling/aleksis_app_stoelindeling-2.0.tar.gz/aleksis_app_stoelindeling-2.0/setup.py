# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.stoelindeling',
 'aleksis.apps.stoelindeling.migrations',
 'aleksis.apps.stoelindeling.util']

package_data = \
{'': ['*'],
 'aleksis.apps.stoelindeling': ['frontend/*',
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
                                'static/*',
                                'static/css/stoelindeling/*',
                                'static/js/stoelindeling/*',
                                'templates/stoelindeling/partials/*',
                                'templates/stoelindeling/seating_plan/*']}

install_requires = \
['aleksis-app-chronos>=3.0,<4.0', 'aleksis-core>=3.0,<4.0']

entry_points = \
{'aleksis.app': ['stoelindeling = '
                 'aleksis.apps.stoelindeling.apps:DefaultConfig']}

setup_kwargs = {
    'name': 'aleksis-app-stoelindeling',
    'version': '2.0',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp Stoelindeling (Create and publish seating plans)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp Stoelindeling (Create and publish seating plans)\n==========================================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\n* Create and manage seating plans for different groups in different rooms.\n* Make these plans available in the class register.\n* Allow customizing plans for individual combinations of groups, subjects and rooms.\n\nLicence\n-------\n\n::\n\n  Copyright © 2022 Jonathan Weth <dev@jonathanweth.de>\n\n  Licenced under the EUPL, version 1.2 or later\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://edugit.org/AlekSIS/AlekSIS\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Jonathan Weth',
    'author_email': 'dev@jonathanweth.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://aleksis.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
