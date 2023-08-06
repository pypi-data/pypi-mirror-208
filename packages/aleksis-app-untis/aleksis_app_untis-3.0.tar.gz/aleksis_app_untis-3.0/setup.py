# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.untis',
 'aleksis.apps.untis.management.commands',
 'aleksis.apps.untis.migrations',
 'aleksis.apps.untis.tests.util',
 'aleksis.apps.untis.util.mysql',
 'aleksis.apps.untis.util.mysql.importers']

package_data = \
{'': ['*'],
 'aleksis.apps.untis': ['locale/ar/LC_MESSAGES/*',
                        'locale/de_DE/LC_MESSAGES/*',
                        'locale/fr/LC_MESSAGES/*',
                        'locale/la/LC_MESSAGES/*',
                        'locale/nb_NO/LC_MESSAGES/*',
                        'locale/ru/LC_MESSAGES/*',
                        'locale/tr_TR/LC_MESSAGES/*',
                        'locale/uk/LC_MESSAGES/*']}

install_requires = \
['aleksis-app-chronos>=3.0,<4.0',
 'aleksis-core>=3.0,<4.0',
 'defusedxml>=0.7.0,<0.8.0',
 'mysqlclient>=2.0.0,<3.0.0',
 'tqdm>=4.44.1,<5.0.0']

entry_points = \
{'aleksis.app': ['untis = aleksis.apps.untis.apps:UntisConfig']}

setup_kwargs = {
    'name': 'aleksis-app-untis',
    'version': '3.0',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp for Untis import',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp for Untis import\n==========================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\n* Import absence reasons\n* Import absences\n* Import breaks\n* Import classes\n* Import events\n* Import exams\n* Import exported Untis database via MySQL import\n* Import exported Untis XML files\n* Import holidays\n* Import lessons\n* Import rooms\n* Import subjects\n* Import substitutions\n* Import supervision areas\n* Import teachers\n* Import time periods\n\nLicence\n-------\n\n::\n\n  Copyright © 2018, 2019, 2020, 2021, 2022 Jonathan Weth <dev@jonathanweth.de>\n  Copyright © 2018, 2019 Frank Poetzsch-Heffter <p-h@katharineum.de>\n  Copyright © 2019, 2020, 2021, 2022 Dominik George <dominik.george@teckids.org>\n  Copyright © 2019, 2020 Tom Teichler <tom.teichler@teckids.org>\n  Copyright © 2019 Julian Leucker <leuckeju@katharineum.de>\n  Copyright © 2019 mirabilos <thorsten.glaser@teckids.org>\n\n  Licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany).\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://aleksis.org/\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Dominik George',
    'author_email': 'dominik.george@teckids.org',
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
