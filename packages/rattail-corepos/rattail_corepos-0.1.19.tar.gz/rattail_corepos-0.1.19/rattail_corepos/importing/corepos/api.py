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
CORE POS (API) -> Rattail data importing
"""

import datetime
import decimal
import logging
from collections import OrderedDict

from sqlalchemy import orm

from rattail import importing
from rattail.gpc import GPC
from rattail.time import localtime, make_utc
from rattail.core import get_uuid
from rattail.db.util import normalize_full_name
from rattail_corepos import importing as corepos_importing
from rattail_corepos.corepos.util import get_core_members
from rattail_corepos.corepos.api import make_corepos_api


log = logging.getLogger(__name__)


class FromCOREPOSToRattail(importing.ToRattailHandler):
    """
    Import handler for data coming from a CORE POS API.
    """
    host_key = 'corepos_api'
    generic_host_title = "CORE Office (API)"
    host_title = "CORE-POS (API)"
    safe_for_web_app = True

    def get_importers(self):
        importers = OrderedDict()
        importers['Customer'] = CustomerImporter
        importers['Person'] = PersonImporter
        importers['CustomerPerson'] = CustomerPersonImporter
        importers['Member'] = MemberImporter
        importers['Store'] = StoreImporter
        importers['Department'] = DepartmentImporter
        importers['Subdepartment'] = SubdepartmentImporter
        importers['Vendor'] = VendorImporter
        importers['Product'] = ProductImporter
        importers['ProductCost'] = ProductCostImporter
        importers['ProductMovement'] = ProductMovementImporter
        return importers

    def get_default_keys(self):
        keys = super(FromCOREPOSToRattail, self).get_default_keys()
        if 'ProductMovement' in keys:
            keys.remove('ProductMovement')
        return keys


class FromCOREPOSAPI(importing.Importer):
    """
    Base class for all CORE POS API data importers.
    """

    def setup(self):
        super(FromCOREPOSAPI, self).setup()
        self.establish_api()

    def datasync_setup(self):
        super(FromCOREPOSAPI, self).datasync_setup()
        self.establish_api()

    def establish_api(self):
        self.api = make_corepos_api(self.config)

    def get_core_members(self):
        return get_core_members(self.config, self.api, progress=self.progress)


class CustomerImporter(FromCOREPOSAPI, corepos_importing.model.CustomerImporter):
    """
    Importer for customer data from CORE POS API.
    """
    key = 'corepos_account_id'
    supported_fields = [
        'corepos_account_id',
        'id',
        'number',
        'name',
        'address_street',
        'address_street2',
        'address_city',
        'address_state',
        'address_zipcode',
    ]

    def get_host_objects(self):
        return self.get_core_members()

    def normalize_host_object(self, member):

        if member['customerAccountID'] == 0:
            log.debug("member %s has customerAccountID of 0: %s",
                      member['cardNo'], member)
            return

        # figure out the "account holder" customer for the member.  note that
        # we only use this to determine the `Customer.name` in Rattail
        customers = member['customers']
        account_holders = [customer for customer in customers
                           if customer['accountHolder']]
        if account_holders:
            if len(account_holders) > 1:
                log.warning("member %s has %s account holders in CORE: %s",
                            member['cardNo'], len(account_holders), member)
            customer = account_holders[0]
        elif customers:
            if len(customers) > 1:
                log.warning("member %s has %s customers but no account holders: %s",
                            member['cardNo'], len(customers), member)
            customer = customers[0]
        else:
            raise NotImplementedError("TODO: how to handle member with no customers?")

        return {
            'corepos_account_id': int(member['customerAccountID']),
            'id': member['customerAccountID'],
            'number': int(member['cardNo']),
            'name': normalize_full_name(customer['firstName'],
                                        customer['lastName']),

            'address_street': member['addressFirstLine'] or None,
            'address_street2': member['addressSecondLine'] or None,
            'address_city': member['city'] or None,
            'address_state': member['state'] or None,
            'address_zipcode': member['zip'] or None,
        }


class PersonImporter(FromCOREPOSAPI, corepos_importing.model.PersonImporter):
    """
    Importer for person data from CORE POS API.
    """
    key = 'corepos_customer_id'
    supported_fields = [
        'corepos_customer_id',
        'first_name',
        'last_name',
        'display_name',
        'customer_uuid',
        'customer_person_ordinal',
        'phone_number',
        'phone_number_2',
        'email_address',
    ]

    def setup(self):
        super(PersonImporter, self).setup()
        model = self.config.get_model()

        self.customers = self.app.cache_model(self.session,
                                              model.Customer,
                                              key='id')

    def get_host_objects(self):

        # first get all member data from CORE API
        members = self.get_core_members()
        normalized = []

        # then collect all the "person" records
        def normalize(member, i):
            normalized.extend(self.get_person_objects_for_member(member))

        self.progress_loop(normalize, members,
                           message="Collecting Person data from CORE")
        return normalized

    def get_person_objects_for_member(self, member):
        """
        Return a list of Person data objects for the given Member.  This
        logic is split out separately so that datasync can leverage it too.
        """
        customers = member['customers']
        people = []

        # make sure account holder is listed first
        account_holder = None
        secondary = False
        mixedup = False
        for customer in customers:
            if customer['accountHolder'] and not secondary:
                account_holder = customer
            elif not customer['accountHolder']:
                secondary = True
            elif customer['accountHolder'] and secondary:
                mixedup = True
        if mixedup:
            raise NotImplementedError("TODO: should re-sort the customers list for member {}".format(member['cardNo']))

        for i, customer in enumerate(customers, 1):
            person = dict(customer)
            person['customer_person_ordinal'] = i
            people.append(person)

        return people

    def get_customer(self, id):
        if hasattr(self, 'customers'):
            return self.customers.get(id)

        model = self.config.get_model()
        try:
            return self.session.query(model.Customer)\
                               .filter(model.Customer.id == id)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def normalize_host_object(self, person):

        customer = self.get_customer(person['customerAccountID'])
        if not customer:
            log.warning("Rattail customer not found for customerAccountID: %s",
                        person['customerAccountID'])
            return

        return {
            'corepos_customer_id': int(person['customerID']),
            'first_name': person['firstName'],
            'last_name': person['lastName'],
            'display_name': normalize_full_name(person['firstName'],
                                                person['lastName']),
            'customer_uuid': customer.uuid,
            'customer_person_ordinal': person['customer_person_ordinal'],
            'phone_number': person['phone'] or None,
            'phone_number_2': person['altPhone'] or None,
            'email_address': person['email'] or None,
        }


class CustomerPersonImporter(FromCOREPOSAPI, importing.model.CustomerPersonImporter):
    """
    Importer for customer-person linkage data from CORE POS API.

    Note that we don't use this one in datasync, it's just for nightly
    double-check.
    """
    key = ('customer_uuid', 'person_uuid')
    supported_fields = [
        'customer_uuid',
        'person_uuid',
        'ordinal',
    ]

    def setup(self):
        super(CustomerPersonImporter, self).setup()
        model = self.config.get_model()

        query = self.session.query(model.Customer)\
                            .join(model.CoreCustomer)
        self.customers = self.app.cache_model(self.session,
                                              model.Customer,
                                              query=query,
                                              key='corepos_account_id')

        query = self.session.query(model.Person)\
                            .join(model.CorePerson)\
                            .filter(model.CorePerson.corepos_customer_id != None)
        self.people = self.app.cache_model(
            self.session,
            model.Person,
            key='corepos_customer_id',
            query=query,
            query_options=[orm.joinedload(model.Person._corepos)])

    def get_host_objects(self):

        # first get all member data from CORE API
        members = self.get_core_members()
        normalized = []

        # then collect all customer/person combination records
        def normalize(member, i):
            # make sure we put the account holder first in the list!
            customers = sorted(member['customers'],
                               key=lambda cust: 1 if cust['accountHolder'] else 0,
                               reverse=True)
            for i, customer in enumerate(customers, 1):
                normalized.append({
                    'customer_account_id': int(member['customerAccountID']),
                    'person_customer_id': customer['customerID'],
                    'ordinal': i,
                })

        self.progress_loop(normalize, members,
                           message="Collecting CustomerPerson data from CORE")
        return normalized

    def get_customer(self, account_id):
        if hasattr(self, 'customers'):
            return self.customers.get(account_id)

        model = self.config.get_model()
        try:
            return self.session.query(model.Customer)\
                               .join(model.CoreCustomer)\
                               .filter(model.CoreCustomer.corepos_account_id == account_id)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def get_person(self, corepos_customer_id):
        if hasattr(self, 'people'):
            return self.people.get(corepos_customer_id)

        model = self.config.get_model()
        try:
            return self.session.query(model.Person)\
                               .join(model.CorePerson)\
                               .filter(model.CorePerson.corepos_customer_id == corepos_customer_id)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def normalize_host_object(self, cp):

        customer = self.get_customer(cp['customer_account_id'])
        if not customer:
            log.warning("Rattail customer not found for customerAccountID: %s",
                        cp['customer_account_id'])
            return

        person = self.get_person(int(cp['person_customer_id']))
        if not person:
            log.warning("Rattail person not found for customerID: %s",
                        cp['person_customer_id'])
            return

        return {
            'customer_uuid': customer.uuid,
            'person_uuid': person.uuid,
            'ordinal': cp['ordinal'],
        }


class StoreImporter(FromCOREPOSAPI, corepos_importing.model.StoreImporter):
    """
    Importer for store data from CORE POS API.
    """
    key = 'corepos_id'
    supported_fields = [
        'corepos_id',
        'id',
        'name',
    ]

    def get_host_objects(self):
        return self.api.get_stores()

    def normalize_host_object(self, store):
        return {
            'corepos_id': int(store['storeID']),
            'id': str(store['storeID']),
            'name': store['description'],
        }


class DepartmentImporter(FromCOREPOSAPI, corepos_importing.model.DepartmentImporter):
    """
    Importer for department data from CORE POS API.
    """
    key = 'corepos_number'
    supported_fields = [
        'corepos_number',
        'number',
        'name',
    ]

    def get_host_objects(self):
        return self.api.get_departments()

    def normalize_host_object(self, department):
        return {
            'corepos_number': int(department['dept_no']),
            'number': int(department['dept_no']),
            'name': department['dept_name'],
        }


class SubdepartmentImporter(FromCOREPOSAPI, corepos_importing.model.SubdepartmentImporter):
    """
    Importer for subdepartment data from CORE POS API.
    """
    key = 'corepos_number'
    supported_fields = [
        'corepos_number',
        'number',
        'name',
        'department_number',
    ]

    def get_host_objects(self):
        return self.api.get_subdepartments()

    def normalize_host_object(self, subdepartment):
        department_number = None
        if 'dept_ID' in subdepartment:
            department_number = int(subdepartment['dept_ID'])

        return {
            'corepos_number': int(subdepartment['subdept_no']),
            'number': int(subdepartment['subdept_no']),
            'name': subdepartment['subdept_name'],
            'department_number': department_number,
        }


class VendorImporter(FromCOREPOSAPI, corepos_importing.model.VendorImporter):
    """
    Importer for vendor data from CORE POS API.
    """
    key = 'corepos_id'
    supported_fields = [
        'corepos_id',
        'id',
        'name',
        'abbreviation',
        'special_discount',
        'phone_number',
        'fax_number',
        'email_address',
    ]

    def get_host_objects(self):
        return self.api.get_vendors()

    def normalize_host_object(self, vendor):
        return {
            'corepos_id': int(vendor['vendorID']),
            'id': str(vendor['vendorID']),
            'name': vendor['vendorName'],
            'abbreviation': vendor.get('vendorAbbreviation') or None,
            'special_discount': decimal.Decimal(vendor['discountRate']),
            'phone_number': vendor.get('phone') or None,
            'fax_number': vendor.get('fax') or None,
            'email_address': vendor.get('email') or None,
        }


class ProductImporter(FromCOREPOSAPI, corepos_importing.model.ProductImporter):
    """
    Importer for product data from CORE POS API.
    """
    key = 'uuid'
    supported_fields = [
        'uuid',
        'corepos_id',
        'item_id',
        'upc',
        'brand_name',
        'description',
        'unit_size',
        'unit_of_measure',
        'uom_abbreviation',
        'size',
        'weighed',
        'department_number',
        'subdepartment_number',
        'regular_price_price',
        'regular_price_multiple',
        'regular_price_type',
        'food_stampable',
        # 'tax1',
        # 'tax2',
        'case_size',
    ]

    def setup(self):
        super(ProductImporter, self).setup()
        model = self.model

        query = self.session.query(model.Product)\
                            .join(model.CoreProduct)\
                            .filter(model.CoreProduct.corepos_id != None)\
                            .options(orm.joinedload(model.Product._corepos))
        self.core_existing = self.app.cache_model(self.session,
                                                  model.Product,
                                                  key='corepos_id',
                                                  query=query)

        self.vendor_items_by_upc = {}

        def cache(item, i):
            self.vendor_items_by_upc.setdefault(item['upc'], []).append(item)

        self.progress_loop(cache, self.api.get_vendor_items(),
                           message="Caching CORE Vendor Items")

    def get_host_objects(self):
        return self.api.get_products()

    def identify_product(self, corepos_product):
        model = self.config.get_model()
        corepos_id = int(corepos_product['id'])

        if hasattr(self, 'core_existing'):
            product = self.core_existing.get(corepos_id)
            if product:
                return product

        else:
            try:
                return self.session.query(model.Product)\
                                   .join(model.CoreProduct)\
                                   .filter(model.CoreProduct.corepos_id == corepos_id)\
                                   .one()
            except orm.exc.NoResultFound:
                pass

        # at this point we'll search by `Product.item_id` instead
        return self.session.query(model.Product)\
                           .outerjoin(model.CoreProduct)\
                           .filter(model.CoreProduct.corepos_id == None)\
                           .filter(model.Product.item_id == corepos_product['upc'])\
                           .first()

    def identify_product_uuid(self, corepos_product):
        product = self.identify_product(corepos_product)
        if product:
            return product.uuid
        return get_uuid()

    def get_vendor_items(self, api_product):
        if hasattr(self, 'vendor_items_by_upc'):
            return self.vendor_items_by_upc.get(api_product['upc'])

        return self.api.get_vendor_items(upc=api_product['upc'])

    def normalize_host_object(self, product):
        try:
            upc = GPC(product['upc'], calc_check_digit='upc')
        except (TypeError, ValueError):
            log.debug("CORE POS product has invalid UPC: %s", product['upc'])
            if len(self.key) == 1 and self.key[0] == 'upc':
                return
            upc = None

        department_number = None
        if 'department' in product:
            department_number = int(product['department']) or None

        subdepartment_number = None
        if 'subdept' in product:
            subdepartment_number = int(product['subdept']) or None

        price = None
        if product.get('normal_price') is not None:
            price = decimal.Decimal(product['normal_price'])

        data = {
            'uuid': self.identify_product_uuid(product),
            'corepos_id': int(product['id']),
            'item_id': product['upc'],
            'upc': upc,
            'brand_name': product.get('brand') or None,
            'description': product.get('description') or '',

            'department_number': department_number,
            'subdepartment_number': subdepartment_number,

            'weighed': product.get('scale') == '1',
            'food_stampable': None,
            # 'tax1': product['tax'] == '1', # TODO: is this right?
            # 'tax2': product['tax'] == '2', # TODO: is this right?

            'regular_price_price': price,
            'regular_price_multiple': 1 if price is not None else None,
            'regular_price_type': self.enum.PRICE_TYPE_REGULAR if price is not None else None,
        }

        if 'foodstamp' in product:
            data['food_stampable'] = product['foodstamp'] == '1'

        if self.fields_active(self.size_fields):
            size_info = self.normalize_size_info(product)
            data.update({
                'size': size_info['size'],
                'unit_size': size_info['unit_size'],
                'unit_of_measure': size_info['uom_code'],
                'uom_abbreviation': size_info['uom_abbrev'],
            })

        if 'case_size' in self.fields:
            case_size = None
            items = self.get_vendor_items(product)
            if items:
                # here we sort by `modified DESC` to get the "deterministic
                # pseudo-default" vendorItems record

                def sortkey(item):
                    modified = item.get('modified')
                    if not modified:
                        return datetime.datetime(1900, 1, 1)
                    dt = datetime.datetime.strptime(modified, '%Y-%m-%d %H:%M:%S')
                    return dt

                items = sorted(items, key=sortkey, reverse=True)
                item = items[0]
                case_size = decimal.Decimal(item['units'])

            data['case_size'] = case_size

        return data


class ProductMovementImporter(FromCOREPOSAPI, corepos_importing.model.ProductImporter):
    """
    Importer for product movement data from CORE POS API.
    """
    key = 'corepos_id'
    supported_fields = [
        'corepos_id',
        'last_sold',
    ]
    allow_create = False
    allow_delete = False

    def get_host_objects(self):
        return self.api.get_products()

    def normalize_host_object(self, product):

        last_sold = None
        if 'last_sold' in product:
            last_sold = datetime.datetime.strptime(product['last_sold'], '%Y-%m-%d %H:%M:%S')
            last_sold = localtime(self.config, last_sold)
            last_sold = make_utc(last_sold)

        return {
            'corepos_id': int(product['id']),
            'last_sold': last_sold,
        }


class ProductCostImporter(FromCOREPOSAPI, corepos_importing.model.ProductCostImporter):
    """
    Importer for product cost data from CORE POS API.
    """
    key = ('vendor_uuid', 'code')
    supported_fields = [
        'corepos_id',
        'product_uuid',
        'vendor_uuid',
        'code',
        'case_size',
        'case_cost',
        'unit_cost',
        'preferred',
    ]

    def setup(self):
        super(ProductCostImporter, self).setup()
        model = self.config.get_model()

        query = self.session.query(model.Vendor)\
                            .join(model.CoreVendor)\
                            .filter(model.CoreVendor.corepos_id != None)
        self.vendors = self.app.cache_model(self.session,
                                            model.Vendor,
                                            query=query,
                                            key='corepos_id')

        self.corepos_products = {}

        def cache(product, i):
            self.corepos_products[product['upc']] = product

        self.progress_loop(cache, self.api.get_products(),
                           message="Caching Products from CORE-POS API")

        self.products_by_item_id = self.app.cache_model(self.session,
                                                        model.Product,
                                                        key='item_id')

    def get_host_objects(self):
        return self.api.get_vendor_items()

    def get_vendor(self, item):
        corepos_id = int(item['vendorID'])

        if hasattr(self, 'vendors'):
            return self.vendors.get(corepos_id)

        model = self.config.get_model()
        try:
            return self.session.query(model.Vendor)\
                               .join(model.CoreVendor)\
                               .filter(model.CoreVendor.corepos_id == corepos_id)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def get_corepos_product(self, item):
        if hasattr(self, 'corepos_products'):
            return self.corepos_products.get(item['upc'])

        return self.api.get_product(item['upc'])

    def get_product(self, item):
        item_id = item['upc']

        if hasattr(self, 'products_by_item_id'):
            return self.products_by_item_id.get(item_id)

        model = self.model
        try:
            return self.session.query(model.Product)\
                               .filter(model.Product.item_id == item_id)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def normalize_host_object(self, item):
        vendor = self.get_vendor(item)
        if not vendor:
            log.warning("CORE POS vendor not found for item: %s", item)
            return

        product = self.get_product(item)
        if not product:
            log.warning("product not found for CORE vendor item: %s", item)
            return

        core_product = self.get_corepos_product(item)
        # if not product:
        #     log.warning("CORE POS product not found for item: %s", item)
        #     return

        preferred = False
        if core_product and core_product['default_vendor_id'] == item['vendorID']:
            preferred = True

        case_size = decimal.Decimal(item['units'])
        unit_cost = decimal.Decimal(item['cost'])

        return {
            'corepos_id': int(item['vendorItemID']),
            'product_uuid': product.uuid,
            'vendor_uuid': vendor.uuid,
            'code': (item['sku'] or '').strip() or None,
            'case_size': case_size,
            'case_cost': case_size * unit_cost,
            'unit_cost': unit_cost,
            'preferred': preferred,
        }


class MemberImporter(FromCOREPOSAPI, corepos_importing.model.MemberImporter):
    """
    Importer for member data from CORE POS API.
    """
    key = 'corepos_account_id'
    supported_fields = [
        'corepos_account_id',
        'number',
        'id',
        'customer_uuid',
        'person_uuid',
        'joined',
        'withdrew',
    ]

    # TODO: should make this configurable
    member_status_codes = [
        'PC',
        'TERM',
    ]

    # TODO: should make this configurable
    non_member_status_codes = [
        'REG',
        'INACT',
    ]

    def setup(self):
        super(MemberImporter, self).setup()
        model = self.config.get_model()
        self.customers = self.app.cache_model(self.session,
                                              model.Customer,
                                              key='number')

    def get_host_objects(self):
        return self.get_core_members()

    def get_customer(self, number):
        if hasattr(self, 'customers'):
            return self.customers.get(number)

        model = self.config.get_model()
        try:
            return self.session.query(model.Customer)\
                               .filter(model.Customer.number == number)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def normalize_host_object(self, member):
        customer = self.get_customer(member['cardNo'])
        if not customer:
            log.warning("Rattail customer not found for cardNo %s: %s",
                        member['cardNo'], member)
            return

        person = customer.first_person()
        if not person:
            log.warning("Rattail person not found for cardNo %s: %s",
                        member['cardNo'], member)
            return

        if member['memberStatus'] in self.non_member_status_codes:
            log.debug("skipping non-member %s with status '%s': %s",
                      member['memberStatus'], member['cardNo'], member)
            return
        if member['memberStatus'] not in self.member_status_codes:
            # note that we will still import this one! we don't skip it
            log.warning("unexpected status '%s' for member %s: %s",
                        member['memberStatus'], member['cardNo'], member)

        joined = None
        if member['startDate'] and member['startDate'] != '0000-00-00 00:00:00':
            joined = datetime.datetime.strptime(member['startDate'],
                                                '%Y-%m-%d %H:%M:%S')
            joined = joined.date()

        withdrew = None
        if member['endDate'] and member['endDate'] != '0000-00-00 00:00:00':
            withdrew = datetime.datetime.strptime(member['endDate'],
                                                  '%Y-%m-%d %H:%M:%S')
            withdrew = withdrew.date()

        return {
            'corepos_account_id': int(member['customerAccountID']),
            'number': int(member['cardNo']),
            'id': str(member['customerAccountID']),
            'customer_uuid': customer.uuid,
            'person_uuid': person.uuid,
            'joined': joined,
            'withdrew': withdrew,
        }
