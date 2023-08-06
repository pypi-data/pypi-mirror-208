# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.chronos',
 'aleksis.apps.chronos.migrations',
 'aleksis.apps.chronos.templatetags',
 'aleksis.apps.chronos.tests',
 'aleksis.apps.chronos.tests.regression',
 'aleksis.apps.chronos.util']

package_data = \
{'': ['*'],
 'aleksis.apps.chronos': ['frontend/*',
                          'frontend/messages/*',
                          'locale/ar/LC_MESSAGES/*',
                          'locale/de_DE/LC_MESSAGES/*',
                          'locale/fr/LC_MESSAGES/*',
                          'locale/la/LC_MESSAGES/*',
                          'locale/nb_NO/LC_MESSAGES/*',
                          'locale/ru/LC_MESSAGES/*',
                          'locale/tr_TR/LC_MESSAGES/*',
                          'locale/uk/LC_MESSAGES/*',
                          'static/css/chronos/*',
                          'static/js/chronos/*',
                          'templates/chronos/*',
                          'templates/chronos/partials/*',
                          'templates/chronos/partials/subs/*']}

install_requires = \
['aleksis-app-resint>=3.0,<4.0',
 'aleksis-core>=3.0,<4.0',
 'calendarweek>=0.5.0,<0.6.0']

entry_points = \
{'aleksis.app': ['chronos = aleksis.apps.chronos.apps:ChronosConfig']}

setup_kwargs = {
    'name': 'aleksis-app-chronos',
    'version': '3.0',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp Χρόνος (digital timetables)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp Χρόνος (digital timetables)\n=====================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\n* Consider object-level rules and permissions\n* Export timetables as PDF\n* Search in rooms\n* Show absent groups in timetable\n* Show absent teachers in timetable\n* Show affected groups in timetable\n* Show affected teachers in timetable\n* Show supervisions in timetable\n* Timetables per day\n* Timetables per group\n* Timetables per person\n* Timetables per room\n* Timetables per week\n* Smart timetable\n\nLicence\n-------\n\n::\n\n  Copyright © 2018, 2019, 2020, 2021, 2022 Jonathan Weth <dev@jonathanweth.de>\n  Copyright © 2018, 2019 Frank Poetzsch-Heffter <p-h@katharineum.de>\n  Copyright © 2019, 2020, 2022 Dominik George <dominik.george@teckids.org>\n  Copyright © 2019, 2021 Hangzhi Yu <yuha@katharineum.de>\n  Copyright © 2019 Julian Leucker <leuckeju@katharineum.de>\n  Copyright © 2019 Tom Teichler <tom.teichler@teckids.org>\n  Copyright © 2021 Lloyd Meins <meinsll@katharineum.de>\n\n  Licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany).\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://aleksis.org/\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Dominik George',
    'author_email': 'dominik.george@teckids.org',
    'maintainer': 'Jonathan Weth',
    'maintainer_email': 'wethjo@katharineum.de',
    'url': 'https://aleksis.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
