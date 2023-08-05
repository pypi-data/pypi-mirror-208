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
Organizational data model extensions
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model


class QuickbooksDepartment(model.Base):
    """
    Quickbooks extensions to core Department model
    """
    __tablename__ = 'quickbooks_department'
    __table_args__ = (
        sa.ForeignKeyConstraint(['uuid'], ['department.uuid'],
                                name='quickbooks_department_fk_department'),
    )
    __versioned__ = {}

    uuid = model.uuid_column(default=None)

    department = orm.relationship(
        model.Department,
        doc="""
        Department to which this extension record pertains.
        """,
        backref=orm.backref(
            '_quickbooks',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Quickbooks extension record for the department.
            """))

    quickbooks_expense_account = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks "expense account" for the department.
    """)

    quickbooks_expense_class = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks "expense class" for the department.
    """)


QuickbooksDepartment.make_proxy(model.Department, '_quickbooks', 'quickbooks_expense_account')
QuickbooksDepartment.make_proxy(model.Department, '_quickbooks', 'quickbooks_expense_class')
