# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.alsijil',
 'aleksis.apps.alsijil.migrations',
 'aleksis.apps.alsijil.templatetags',
 'aleksis.apps.alsijil.tests',
 'aleksis.apps.alsijil.util']

package_data = \
{'': ['*'],
 'aleksis.apps.alsijil': ['frontend/*',
                          'frontend/messages/*',
                          'locale/ar/LC_MESSAGES/*',
                          'locale/de_DE/LC_MESSAGES/*',
                          'locale/fr/LC_MESSAGES/*',
                          'locale/la/LC_MESSAGES/*',
                          'locale/nb_NO/LC_MESSAGES/*',
                          'locale/ru/LC_MESSAGES/*',
                          'locale/tr_TR/LC_MESSAGES/*',
                          'locale/uk/LC_MESSAGES/*',
                          'static/css/alsijil/*',
                          'static/js/alsijil/*',
                          'templates/alsijil/absences/*',
                          'templates/alsijil/class_register/*',
                          'templates/alsijil/excuse_type/*',
                          'templates/alsijil/extra_mark/*',
                          'templates/alsijil/group_role/*',
                          'templates/alsijil/group_role/partials/*',
                          'templates/alsijil/notifications/*',
                          'templates/alsijil/partials/*',
                          'templates/alsijil/partials/lesson/*',
                          'templates/alsijil/partials/lesson/tabs/*',
                          'templates/alsijil/print/*']}

install_requires = \
['aleksis-app-chronos>=3.0,<4.0', 'aleksis-core>=3.0,<4.0']

extras_require = \
{'seatingplans': ['aleksis-app-stoelindeling>=2.0,<3.0']}

entry_points = \
{'aleksis.app': ['alsijil = aleksis.apps.alsijil.apps:AlsijilConfig']}

setup_kwargs = {
    'name': 'aleksis-app-alsijil',
    'version': '3.0',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp كتاب السجل (class register and school records)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp كتاب السجل (class register and school records)\n========================================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\nThis AlekSIS app currently provides the following features for managing digital class registers:\n\n* For users:\n\n * Manage and assign group roles\n * Manage custom excuse types\n * Manage extra marks (e. g. forgotten homework)\n * Manage group notes for every lesson\n * Manage lesson documentations for every lesson\n * Manage personal notes for every lesson\n * Show all owned groups of the current person\n * Show all students of the current person\n * Show filterable (week) overview for lesson documentations and personal/group notes\n * Manage absence of persons\n * Show overview of all students with statistics\n \n\nLicence\n-------\n\n::\n\n  Copyright © 2019, 2021 Dominik George <dominik.george@teckids.org>\n  Copyright © 2019, 2020 Tom Teichler <tom.teichler@teckids.org>\n  Copyright © 2019 mirabilos <thorsten.glaser@teckids.org>\n  Copyright © 2020, 2021, 2022 Jonathan Weth <dev@jonathanweth.de>\n  Copyright © 2020, 2021 Julian Leucker <leuckeju@katharineum.de>\n  Copyright © 2020, 2022 Hangzhi Yu <yuha@katharineum.de>\n  Copyright © 2021 Lloyd Meins <meinsll@katharineum.de>\n\n\n  Licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany).\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://edugit.org/AlekSIS/Official/AlekSIS\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Dominik George',
    'author_email': 'dominik.george@teckids.org',
    'maintainer': 'Dominik George',
    'maintainer_email': 'dominik.george@teckids.org',
    'url': 'https://aleksis.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
