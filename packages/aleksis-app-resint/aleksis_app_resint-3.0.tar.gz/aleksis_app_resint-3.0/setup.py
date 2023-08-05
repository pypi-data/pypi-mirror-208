# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis', 'aleksis.apps.resint', 'aleksis.apps.resint.migrations']

package_data = \
{'': ['*'],
 'aleksis.apps.resint': ['frontend/*',
                         'frontend/messages/*',
                         'locale/ar/LC_MESSAGES/*',
                         'locale/de_DE/LC_MESSAGES/*',
                         'locale/fr/LC_MESSAGES/*',
                         'locale/la/LC_MESSAGES/*',
                         'locale/nb_NO/LC_MESSAGES/*',
                         'locale/ru/LC_MESSAGES/*',
                         'locale/tr_TR/LC_MESSAGES/*',
                         'locale/uk/LC_MESSAGES/*',
                         'templates/resint/group/*',
                         'templates/resint/live_document/*',
                         'templates/resint/poster/*']}

install_requires = \
['AlekSIS-Core>=3.0,<4.0']

entry_points = \
{'aleksis.app': ['resint = aleksis.apps.resint.apps:ResintConfig']}

setup_kwargs = {
    'name': 'aleksis-app-resint',
    'version': '3.0',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp Resint (Public poster)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp Resint (Public poster)\n================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\nThe Resint app provides an interface for uploading PDF posters attached by a calendar week in which this poster is valid.\nThe app provides a public URL `current.pdf` which always returns the current poster PDF and adds a poster item linked to\nthe same URL.\n\nAdditionally, it provides data models and update logic for so-called live documents which are periodically updated PDF files.\n\nLicence\n-------\n\n::\n\n  Copyright © 2018, 2019, 2020, 2021 Jonathan Weth <dev@jonathanweth.de>\n  Copyright © 2019 Julian Leucker <leuckeju@katharineum.de>\n  Copyright © 2020, 2021 Frank Poetzsch-Heffter <p-h@katharineum.de>\n  Copyright © 2022 Dominik George <dominik.george@teckids.org>\n\n  Licenced under the EUPL, version 1.2 or later\n\nPlease see the LICENCE file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://edugit.org/AlekSIS/official/AlekSIS\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Julian Leucker',
    'author_email': 'leuckeju@katharineum.de',
    'maintainer': 'Jonathan Weth',
    'maintainer_email': 'dev@jonathanweth.de',
    'url': 'https://aleksis.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
