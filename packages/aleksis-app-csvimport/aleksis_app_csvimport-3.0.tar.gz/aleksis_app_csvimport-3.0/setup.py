# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.csv_import',
 'aleksis.apps.csv_import.management.commands',
 'aleksis.apps.csv_import.migrations',
 'aleksis.apps.csv_import.tests',
 'aleksis.apps.csv_import.tests.models',
 'aleksis.apps.csv_import.tests.util',
 'aleksis.apps.csv_import.util']

package_data = \
{'': ['*'],
 'aleksis.apps.csv_import': ['frontend/*',
                             'frontend/messages/*',
                             'locale/ar/LC_MESSAGES/*',
                             'locale/de_DE/LC_MESSAGES/*',
                             'locale/fr/LC_MESSAGES/*',
                             'locale/la/LC_MESSAGES/*',
                             'locale/nb_NO/LC_MESSAGES/*',
                             'locale/ru/LC_MESSAGES/*',
                             'locale/tr_TR/LC_MESSAGES/*',
                             'locale/uk/LC_MESSAGES/*',
                             'templates/csv_import/*',
                             'templates/csv_import/import_template/*']}

install_requires = \
['aleksis-core>=3.0,<4.0',
 'chardet>=5.0.0,<6.0.0',
 'dateparser>=1.0.0,<2.0.0',
 'pandas>=1.0.0,<2.0.0',
 'phonenumbers>=8.10,<9.0',
 'ruamel.yaml>=0.17.19,<0.18.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'aleksis.app': ['csv_import = aleksis.apps.csv_import.apps:CSVImportConfig']}

setup_kwargs = {
    'name': 'aleksis-app-csvimport',
    'version': '3.0',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp for CSV import',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp for CSV imports\n====================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\nThis app provides general CSV imports functions to interact with school administration software.\n\n* Generic and customisable importer based on templates\n* Register import templates in the frontend\n\nSupported systems:\n\n* Schild-NRW (North Rhine-Westphalia, Germany)\n* Pedasos (Schleswig-Holstein, Germany\n\nLicence\n-------\n\n::\n\n  Copyright © 2019, 2020, 2022 Dominik George <dominik.george@teckids.org>\n  Copyright © 2020, 2021, 2022 Jonathan Weth <dev@jonathanweth.de>\n  Copyright © 2019 mirabilos <thorsten.glaser@teckids.org>\n  Copyright © 2019 Tom Teichler <tom.teichler@teckids.org>\n  Copyright © 2022 magicfelix <felix@felix-zauberer.de>\n\n  Licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany).\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://edugit.org/AlekSIS/AlekSIS\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Dominik George',
    'author_email': 'dominik.george@teckids.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://aleksis.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
