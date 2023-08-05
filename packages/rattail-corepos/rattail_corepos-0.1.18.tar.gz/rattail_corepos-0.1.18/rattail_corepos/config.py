# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
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
"""
Rattail-COREPOS Config Extension
"""

import warnings

from rattail.config import ConfigExtension
from rattail.db.config import get_engines


class RattailCOREPOSExtension(ConfigExtension):
    """
    Config extension for Rattail-COREPOS
    """
    key = 'rattail-corepos'

    def configure(self, config):

        # show deprecation warnings by default, when they occur in corepos
        # (nb. rattail_corepos warnings are already shown, per rattail)
        warnings.filterwarnings('default', category=DeprecationWarning,
                                module=r'^corepos')

        # office_op
        from corepos.db.office_op import Session
        engines = get_engines(config, section='corepos.db.office_op')
        config.core_office_op_engines = engines
        config.core_office_op_engine = engines.get('default')
        Session.configure(bind=config.core_office_op_engine)
        # TODO: deprecate / remove these next 2 lines
        config.corepos_engines = engines
        config.corepos_engine = engines.get('default')

        # office_trans
        from corepos.db.office_trans import Session
        engines = get_engines(config, section='corepos.db.office_trans')
        config.core_office_trans_engines = engines
        config.core_office_trans_engine = engines.get('default')
        Session.configure(bind=config.core_office_trans_engine)
        # TODO: deprecate / remove these next 2 lines
        config.coretrans_engines = engines
        config.coretrans_engine = engines.get('default')

        # office_trans_archive
        from corepos.db.office_trans_archive import Session
        engines = get_engines(config, section='corepos.db.office_trans_archive')
        config.core_office_trans_archive_engines = engines
        config.core_office_trans_archive_engine = engines.get('default')
        Session.configure(bind=config.core_office_trans_archive_engine)

        # lane_op
        from corepos.db.lane_op import Session
        engines = get_engines(config, section='corepos.db.lane_op')
        config.core_lane_op_engines = engines
        config.core_lane_op_engine = engines.get('default')
        Session.configure(bind=config.core_lane_op_engine)

        ##############################
        # import handlers
        ##############################

        # rattail corepos-import-square
        config.setdefault('rattail.importing', 'to_corepos_db_office_trans.from_square_csv.import.default_handler',
                          'rattail_corepos.corepos.importing.db.square:FromSquareToCoreTrans')
        config.setdefault('rattail.importing', 'to_corepos_db_office_trans.from_square_csv.import.default_cmd',
                          'rattail corepos-import-square')
        # TODO: there was not a legacy setting in place for this one
        # config.setdefault('rattail.importing', 'to_corepos_db_office_trans.from_square_csv.import.legacy_handler_setting',
        #                   'corepos.importing, square.handler')

        # rattail export-corepos
        config.setdefault('rattail.importing', 'to_corepos_api.from_rattail.export.default_handler',
                          'rattail_corepos.corepos.importing.rattail:FromRattailToCore')
        config.setdefault('rattail.importing', 'to_corepos_api.from_rattail.export.default_cmd',
                          'rattail export-corepos')
        config.setdefault('rattail.importing', 'to_corepos_api.from_rattail.export.legacy_handler_setting',
                          'rattail.exporting, corepos.handler')

        # rattail import-corepos-api
        config.setdefault('rattail.importing', 'to_rattail.from_corepos_api.import.default_handler',
                          'rattail_corepos.importing.corepos.api:FromCOREPOSToRattail')
        config.setdefault('rattail.importing', 'to_rattail.from_corepos_api.import.default_cmd',
                          'rattail import-corepos-api')
        config.setdefault('rattail.importing', 'to_rattail.from_corepos_api.import.legacy_handler_setting',
                          'rattail.importing, corepos_api.handler')

        # rattail import-corepos-db
        config.setdefault('rattail.importing', 'to_rattail.from_corepos_db_office_op.import.default_handler',
                          'rattail_corepos.importing.corepos.db:FromCOREPOSToRattail')
        config.setdefault('rattail.importing', 'to_rattail.from_corepos_db_office_op.import.default_cmd',
                          'rattail import-corepos-db')
        config.setdefault('rattail.importing', 'to_rattail.from_corepos_db_office_op.import.legacy_handler_setting',
                          'rattail.importing, corepos.handler')

        # trainwreck import-corepos
        config.setdefault('rattail.importing', 'to_trainwreck.from_corepos_db_office_trans.import.default_handler',
                          'rattail_corepos.trainwreck.importing.corepos:FromCoreToTrainwreck')
        config.setdefault('rattail.importing', 'to_trainwreck.from_corepos_db_office_trans.import.default_cmd',
                          'trainwreck import-corepos')
        # TODO: there was not a legacy setting in place for this one
        # config.setdefault('rattail.importing', 'to_trainwreck.from_corepos_db_office_trans.import.legacy_handler_setting',
        #                   'trainwreck.importing, corepos.handler')

        # core-office export-lane-op
        config.setdefault('rattail.importing', 'to_corepos_db_lane_op.from_corepos_db_office_op.export.default_handler',
                          'rattail_corepos.corepos.lane.importing.op.office:FromCoreOfficeToCoreLane')
        config.setdefault('rattail.importing', 'to_corepos_db_lane_op.from_corepos_db_office_op.export.default_cmd',
                          'core-office export-lane-op')
        config.setdefault('rattail.importing', 'to_corepos_db_lane_op.from_corepos_db_office_op.export.legacy_setting',
                          'corepos.lane.importing, office.handler')

        # crepes export-core
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_corepos_db_office_op.export.default_handler',
                          'rattail_corepos.corepos.importing.db.corepos:FromCoreToCoreExport')
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_corepos_db_office_op.export.default_cmd',
                          'crepes export-core')
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_corepos_db_office_op.export.legacy_setting',
                          'rattail_corepos.exporting, corepos.handler')

        # crepes export-csv
        config.setdefault('rattail.importing', 'to_csv.from_corepos_db_office_op.export.default_handler',
                          'rattail_corepos.corepos.importing.db.exporters.csv:FromCoreToCSV')
        config.setdefault('rattail.importing', 'to_csv.from_corepos_db_office_op.export.default_cmd',
                          'crepes export-csv')
        config.setdefault('rattail.importing', 'to_csv.from_corepos_db_office_op.export.legacy_setting',
                          'rattail_corepos.exporting, csv.handler')

        # crepes import-core
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_corepos_db_office_op.import.default_handler',
                          'rattail_corepos.corepos.importing.db.corepos:FromCoreToCoreImport')
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_corepos_db_office_op.import.default_cmd',
                          'crepes import-core')
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_corepos_db_office_op.import.legacy_setting',
                          'rattail_corepos.importing, corepos.handler')

        # crepes import-csv
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_csv.import.default_handler',
                          'rattail_corepos.corepos.importing.db.csv:FromCSVToCore')
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_csv.import.default_cmd',
                          'crepes import-csv')
        config.setdefault('rattail.importing', 'to_corepos_db_office_op.from_csv.import.legacy_setting',
                          'rattail_corepos.importing, csv.handler')

        ##############################
        # batch handlers
        ##############################

        # corepos_member
        config.setdefault('rattail.batch', 'corepos_member.handler.default',
                          'rattail_corepos.batch.coremember:CoreMemberBatchHandler')


def core_office_url(config, require=False, **kwargs):
    """
    Returns the base URL for the CORE Office web app.  Note that this URL will
    *not* have a trailing slash.
    """
    args = ['corepos', 'office.url']
    if require:
        url = config.require(*args, **kwargs)
        return url.rstrip('/')
    else:
        url = config.get(*args, **kwargs)
        if url:
            return url.rstrip('/')


def core_office_customer_account_url(config, card_number, office_url=None):
    """
    Returns the CORE Office URL for the customer account with the given card
    number.
    """
    if not office_url:
        office_url = core_office_url(config, require=True)
    return '{}/mem/MemberEditor.php?memNum={}'.format(
        office_url, card_number)
