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
Store data model extensions
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model


class QuickbooksStore(model.Base):
    """
    Quickbooks extensions to core Store model
    """
    __tablename__ = 'quickbooks_store'
    __table_args__ = (
        sa.ForeignKeyConstraint(['uuid'], ['store.uuid'],
                                name='quickbooks_store_fk_store'),
    )
    __versioned__ = {}

    uuid = model.uuid_column(default=None)

    store = orm.relationship(
        model.Store,
        doc="""
        Store to which this extension record pertains.
        """,
        backref=orm.backref(
            '_quickbooks',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Quickbooks extension record for the store.
            """))

    quickbooks_location = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks "location" for the store.
    """)


QuickbooksStore.make_proxy(model.Store, '_quickbooks', 'quickbooks_location')
