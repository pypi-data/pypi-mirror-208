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
CORE POS (DB) -> Rattail data importing
"""

import decimal
from collections import OrderedDict

from corepos.db.office_op import model as corepos, Session as CoreSession

from rattail import importing
from rattail.gpc import GPC
from rattail_corepos import importing as corepos_importing


class FromCOREPOSToRattail(importing.FromSQLAlchemyHandler, importing.ToRattailHandler):
    """
    Import handler for data coming from a CORE POS database.
    """
    generic_host_title = 'CORE Office (DB "op")'
    host_key = 'corepos_db_office_op'
    corepos_dbkey = 'default'

    @property
    def host_title(self):
        return "CORE-POS (DB/{})".format(self.corepos_dbkey)

    def make_host_session(self):
        return CoreSession(bind=self.config.corepos_engines[self.corepos_dbkey])

    def get_importers(self):
        importers = OrderedDict()
        importers['Vendor'] = VendorImporter
        importers['Department'] = DepartmentImporter
        importers['Subdepartment'] = SubdepartmentImporter
        importers['Product'] = ProductImporter
        return importers


class FromCOREPOS(importing.FromSQLAlchemy):
    """
    Base class for all CORE POS data importers.
    """


class VendorImporter(FromCOREPOS, corepos_importing.model.VendorImporter):
    """
    Importer for vendor data from CORE POS.
    """
    host_model_class = corepos.Vendor
    key = 'corepos_id'
    supported_fields = [
        'corepos_id',
        'name',
        'abbreviation',
        'special_discount',
        'phone_number',
        'fax_number',
        'email_address',
    ]

    def cache_query(self):
        """
        Return the query to be used when caching "local" data.
        """
        # can't just use rattail.db.model b/c the CoreVendor would normally not
        # be in there!  this still requires custom model to be configured though.
        model = self.config.get_model()

        # first get default query
        query = super(VendorImporter, self).cache_query()

        # maybe filter a bit, to ensure only "relevant" records are involved
        if 'corepos_id' in self.key:
            # note, the filter is probably redundant since we INNER JOIN on the
            # extension table, and it doesn't allow null ID values.  but clarity.
            query = query.join(model.CoreVendor)\
                         .filter(model.CoreVendor.corepos_id != None)

        return query

    def normalize_host_object(self, vendor):

        special_discount = None
        if vendor.discount_rate is not None:
            special_discount = decimal.Decimal('{:0.3f}'.format(vendor.discount_rate))

        return {
            'corepos_id': vendor.id,
            'name': vendor.name,
            'abbreviation': vendor.abbreviation or None,
            'special_discount': special_discount,
            'phone_number': vendor.phone or None,
            'fax_number': vendor.fax or None,
            'email_address': vendor.email or None,
        }


class DepartmentImporter(FromCOREPOS, corepos_importing.model.DepartmentImporter):
    """
    Importer for department data from CORE POS.
    """
    host_model_class = corepos.Department
    key = 'corepos_number'
    supported_fields = [
        'corepos_number',
        'number',
        'name',
    ]

    def normalize_host_object(self, department):
        return {
            'corepos_number': department.number,
            'number': department.number,
            'name': department.name,
        }


class SubdepartmentImporter(FromCOREPOS, corepos_importing.model.SubdepartmentImporter):
    """
    Importer for subdepartment data from CORE POS.
    """
    host_model_class = corepos.Subdepartment
    key = 'corepos_number'
    supported_fields = [
        'corepos_number',
        'number',
        'name',
        'department_number',
    ]

    def normalize_host_object(self, subdepartment):
        return {
            'corepos_number': subdepartment.number,
            'number': subdepartment.number,
            'name': subdepartment.name,
            'department_number': subdepartment.department_number,
        }


class ProductImporter(FromCOREPOS, corepos_importing.model.ProductImporter):
    """
    Importer for product data from CORE POS.
    """
    host_model_class = corepos.Product
    key = 'corepos_id'
    supported_fields = [
        'corepos_id',
        'item_id',
        'upc',
        'brand_name',
        'description',
        'size',
        'unit_size',
        'unit_of_measure',
        'uom_abbreviation',
        'weighed',
        'department_number',
        'subdepartment_number',
        'regular_price_price',
        'regular_price_multiple',
        'regular_price_type',
        'food_stampable',
        # 'tax1',
    ]

    def normalize_host_object(self, product):

        try:
            upc = GPC(product.upc, calc_check_digit='upc')
        except (TypeError, ValueError):
            log.debug("CORE POS product has invalid UPC: %s", product.upc)
            if len(self.key) == 1 and self.key[0] == 'upc':
                return
            upc = None

        price = None
        if product.normal_price is not None:
            price = decimal.Decimal('{:03f}'.format(product.normal_price))

        data = {
            'corepos_id': product.id,
            'item_id': product.upc,
            'upc': upc,
            'brand_name': (product.brand or '').strip() or None,
            'description': (product.description or '').strip(),

            'department_number': product.department_number or None,
            'subdepartment_number': product.subdepartment_number or None,

            'weighed': bool(product.scale),
            'food_stampable': product.foodstamp,
            # 'tax1': bool(product.tax), # TODO: is this right?

            'regular_price_price': price,
            'regular_price_multiple': 1 if price is not None else None,
            'regular_price_type': self.enum.PRICE_TYPE_REGULAR if price is not None else None,
        }

        if self.fields_active(self.size_fields):
            size_info = self.normalize_size_info(product)
            data.update({
                'size': size_info['size'],
                'unit_size': size_info['unit_size'],
                'unit_of_measure': size_info['uom_code'],
                'uom_abbreviation': size_info['uom_abbrev'],
            })

        return data
