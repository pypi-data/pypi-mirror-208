# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Vendor data model extensions
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model


class QuickbooksVendor(model.Base):
    """
    Quickbooks extensions to core Vendor model
    """
    __tablename__ = 'quickbooks_vendor'
    __table_args__ = (
        sa.ForeignKeyConstraint(['uuid'], ['vendor.uuid'],
                                name='quickbooks_vendor_fk_vendor'),
    )
    __versioned__ = {}

    uuid = model.uuid_column(default=None)

    vendor = orm.relationship(
        model.Vendor,
        doc="""
        Vendor to which this extension record pertains.
        """,
        backref=orm.backref(
            '_quickbooks',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Quickbooks extension record for the vendor.
            """))

    quickbooks_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks "name" for the vendor.
    """)

    quickbooks_bank_account = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks "bank account" for the vendor.
    """)

    quickbooks_terms = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks "terms" for the vendor.
    """)


QuickbooksVendor.make_proxy(model.Vendor, '_quickbooks', 'quickbooks_name')
QuickbooksVendor.make_proxy(model.Vendor, '_quickbooks', 'quickbooks_bank_account')
QuickbooksVendor.make_proxy(model.Vendor, '_quickbooks', 'quickbooks_terms')
