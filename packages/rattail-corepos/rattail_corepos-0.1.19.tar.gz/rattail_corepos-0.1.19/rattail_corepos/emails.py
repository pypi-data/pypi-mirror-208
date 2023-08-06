# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
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
Email profiles for Rattail / CORE-POS integration
"""

from rattail.emails import ImporterEmail


class core_office_export_lane_op_updates(ImporterEmail):
    """
    Sent when a CORE Office -> CORE Lane export involves data changes.
    """
    handler_spec = 'rattail_corepos.corepos.lane.importing.op.office:FromCoreOfficeToCoreLane'
    abstract = False


class rattail_import_corepos_api_updates(ImporterEmail):
    """
    Sent when a CORE-POS API -> Rattail import involves data changes.
    """
    handler_spec = 'rattail_corepos.importing.corepos.api:FromCOREPOSToRattail'
    abstract = False


class rattail_import_corepos_db_updates(ImporterEmail):
    """
    Sent when a CORE-POS DB -> Rattail import involves data changes.
    """
    handler_spec = 'rattail_corepos.importing.corepos.db:FromCOREPOSToRattail'
    abstract = False
