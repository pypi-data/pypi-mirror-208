# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, 'rattail_corepos', '_version.py')).read())
README = open(os.path.join(here, 'README.rst')).read()


requires = [
    #
    # Version numbers within comments below have specific meanings.
    # Basically the 'low' value is a "soft low," and 'high' a "soft high."
    # In other words:
    #
    # If either a 'low' or 'high' value exists, the primary point to be
    # made about the value is that it represents the most current (stable)
    # version available for the package (assuming typical public access
    # methods) whenever this project was started and/or documented.
    # Therefore:
    #
    # If a 'low' version is present, you should know that attempts to use
    # versions of the package significantly older than the 'low' version
    # may not yield happy results.  (A "hard" high limit may or may not be
    # indicated by a true version requirement.)
    #
    # Similarly, if a 'high' version is present, and especially if this
    # project has laid dormant for a while, you may need to refactor a bit
    # when attempting to support a more recent version of the package.  (A
    # "hard" low limit should be indicated by a true version requirement
    # when a 'high' version is present.)
    #
    # In any case, developers and other users are encouraged to play
    # outside the lines with regard to these soft limits.  If bugs are
    # encountered then they should be filed as such.
    #
    # package                           # low                   high

    'pyCOREPOS',                        # 0.1.0
    'rattail',                          # 0.9.7
]


setup(
    name = "rattail_corepos",
    version = __version__,
    author = "Lance Edgar",
    author_email = "lance@edbob.org",
    url = "https://rattailproject.org/",
    license = "GNU GPL v3",
    description = "Rattail Software Interfaces for CORE POS",
    long_description = README,

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    install_requires = requires,
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,

    entry_points = {

        'console_scripts': [
            'crepes = rattail_corepos.corepos.commands:main',
            'core-office = rattail_corepos.corepos.office.commands:main',
        ],

        'core_office.commands': [
            'export-lane-op = rattail_corepos.corepos.office.commands:ExportLaneOp',
        ],

        'crepes.commands': [
            'export-core = rattail_corepos.corepos.commands:ExportCore',
            'export-csv = rattail_corepos.corepos.commands:ExportCSV',
            'import-core = rattail_corepos.corepos.commands:ImportCore',
            'import-csv = rattail_corepos.corepos.commands:ImportCSV',
        ],

        'rattail.config.extensions': [
            'rattail-corepos = rattail_corepos.config:RattailCOREPOSExtension',
        ],

        'rattail.commands': [
            'export-corepos = rattail_corepos.commands:ExportCore',
            'corepos-import-square = rattail_corepos.commands:CoreImportSquare',
            'import-corepos-api = rattail_corepos.commands:ImportCOREPOSAPI',
            'import-corepos-db = rattail_corepos.commands:ImportCOREPOSDB',
        ],

        'rattail.importing': [
            'to_rattail.from_corepos_api.import = rattail_corepos.importing.corepos.api:FromCOREPOSToRattail',
            'to_rattail.from_corepos_db_office_op.import = rattail_corepos.importing.corepos.db:FromCOREPOSToRattail',
            'to_corepos_api.from_rattail.export = rattail_corepos.corepos.importing.rattail:FromRattailToCore',
            'to_corepos_db_lane_op.from_corepos_db_office_op.export = rattail_corepos.corepos.lane.importing.op.office:FromCoreOfficeToCoreLane',
            'to_trainwreck.from_corepos_db_office_trans = rattail_corepos.trainwreck.importing.corepos:FromCoreToTrainwreck',
        ],

        'trainwreck.commands': [
            'import-corepos = rattail_corepos.trainwreck.commands:ImportCore',
        ],
    },

)
