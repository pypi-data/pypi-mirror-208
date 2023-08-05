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
Database schema extensions for CORE-POS integration
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model


class CorePerson(model.Base):
    """
    CORE-specific extensions to :class:`rattail:rattail.db.model.Person`.
    """
    __tablename__ = 'corepos_person'
    __table_args__ = (
        sa.ForeignKeyConstraint(['uuid'], ['person.uuid'],
                                name='corepos_person_fk_person'),
    )
    __versioned__ = {}

    uuid = model.uuid_column(default=None)
    person = orm.relationship(
        model.Person,
        doc="""
        Reference to the actual person record, which this one extends.
        """,
        backref=orm.backref(
            '_corepos',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Reference to the CORE-POS extension record for this person.
            """))

    corepos_customer_id = sa.Column(sa.Integer(), nullable=False, doc="""
    ``Customers.customerID`` value for this person, within CORE-POS.
    """)

    def __str__(self):
        return str(self.person)

CorePerson.make_proxy(model.Person, '_corepos', 'corepos_customer_id')


class CoreCustomer(model.Base):
    """
    CORE-specific extensions to :class:`rattail:rattail.db.model.Customer`.
    """
    __tablename__ = 'corepos_customer'
    __table_args__ = (
        sa.ForeignKeyConstraint(['uuid'], ['customer.uuid'],
                                name='corepos_customer_fk_customer'),
    )
    __versioned__ = {}

    uuid = model.uuid_column(default=None)
    customer = orm.relationship(
        model.Customer,
        doc="""
        Reference to the actual customer record, which this one extends.
        """,
        backref=orm.backref(
            '_corepos',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Reference to the CORE-POS extension record for this customer.
            """))

    corepos_account_id = sa.Column(sa.Integer(), nullable=False, doc="""
    ``Customers.customerAccountID`` value for this customer, within CORE-POS.
    """)

    def __str__(self):
        return str(self.customer)

CoreCustomer.make_proxy(model.Customer, '_corepos', 'corepos_account_id')


class CoreMember(model.Base):
    """
    CORE-specific extensions to :class:`rattail:rattail.db.model.Member`.
    """
    __tablename__ = 'corepos_member'
    __table_args__ = (
        sa.ForeignKeyConstraint(['uuid'], ['member.uuid'],
                                name='corepos_member_fk_member'),
    )
    __versioned__ = {}

    uuid = model.uuid_column(default=None)
    member = orm.relationship(
        model.Member,
        doc="""
        Reference to the actual member record, which this one extends.
        """,
        backref=orm.backref(
            '_corepos',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Reference to the CORE-POS extension record for this member.
            """))

    corepos_account_id = sa.Column(sa.Integer(), nullable=False, doc="""
    ``Customers.customerAccountID`` value for this member, within CORE-POS.
    """)

    def __str__(self):
        return str(self.member)

CoreMember.make_proxy(model.Member, '_corepos', 'corepos_account_id')
