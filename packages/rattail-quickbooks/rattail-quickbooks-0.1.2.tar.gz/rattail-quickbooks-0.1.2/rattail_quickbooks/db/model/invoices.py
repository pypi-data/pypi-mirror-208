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
Invoice data models
"""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model
from rattail.db.core import filename_column


class QuickbooksExportableInvoice(model.Base):
    """
    Represents a vendor invoice capable of being exported to Quickbooks.
    """
    __tablename__ = 'quickbooks_exportable_invoice'
    __table_args__ = (
        sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'],
                                name='quickbooks_exportable_invoice_fk_store'),
        sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'],
                                name='quickbooks_exportable_invoice_fk_vendor'),
        sa.ForeignKeyConstraint(['deleted_by_uuid'], ['user.uuid'],
                                name='quickbooks_exportable_invoice_fk_deleted_by'),
        sa.ForeignKeyConstraint(['exported_by_uuid'], ['user.uuid'],
                                name='quickbooks_exportable_invoice_fk_exported_by'),
    )
    __versioned__ = {}

    STATUS_NOT_YET_REFRESHED            = 1
    STATUS_EXPORTABLE                   = 2
    STATUS_STORE_NOT_FOUND              = 3
    STATUS_VENDOR_NOT_FOUND             = 4
    STATUS_VENDOR_BAD_INFO              = 5
    STATUS_PO_NOT_FOUND                 = 6
    STATUS_PO_BAD_INFO                  = 7
    STATUS_DIST_PROBLEMS                = 8
    STATUS_DEPTS_IGNORED                = 9
    STATUS_EXPORTED                     = 10
    STATUS_DELETED                      = 11

    STATUS = OrderedDict([
        (STATUS_NOT_YET_REFRESHED,      "data not yet refreshed"),
        (STATUS_EXPORTABLE,             "exportable"),
        (STATUS_STORE_NOT_FOUND,        "store not found"),
        (STATUS_VENDOR_NOT_FOUND,       "vendor not found"),
        (STATUS_VENDOR_BAD_INFO,        "vendor info is invalid"),
        (STATUS_PO_NOT_FOUND,           "PO not found"),
        (STATUS_PO_BAD_INFO,            "PO info is invalid"),
        (STATUS_DIST_PROBLEMS,          "see distribution problem(s)"),
        (STATUS_DEPTS_IGNORED,          "all departments ignored"),
        (STATUS_EXPORTED,               "exported"),
        (STATUS_DELETED,                "deleted"),
    ])

    uuid = model.uuid_column()

    ##################################################
    # columns whose values come from source data
    ##################################################

    store_id = sa.Column(sa.String(length=4), nullable=True, doc="""
    ID string for the store which must pay the invoice.
    """)

    vendor_id = sa.Column(sa.String(length=14), nullable=True, doc="""
    ID string for the vendor which sent the invoice.
    """)

    txn_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    ID string for the transaction represented by the invoice, if
    applicable.
    """)

    invoice_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Invoice number, per source data.
    """)

    invoice_date = sa.Column(sa.Date(), nullable=True, doc="""
    Date of the invoice, per source data.
    """)

    invoice_total = sa.Column(sa.Numeric(precision=8, scale=2), nullable=False, doc="""
    Total amount for the invoice, per source data.
    """)

    shipping_amount = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Amount of the invoice total, which is deemed a "shipping" cost.
    """)

    supplies_amount = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Amount of the invoice total, which is deemed a "supplies" cost.
    """)

    ##################################################
    # columns whose values come from data refresh
    ##################################################

    store_uuid = sa.Column(sa.String(length=32), nullable=True)
    store = orm.relationship(
        model.Store,
        doc="""
        Reference to the :class:`rattail:~rattail.db.model.Store`
        instance associated with the invoice, or ``None``.
        """)

    vendor_uuid = sa.Column(sa.String(length=32), nullable=True)
    vendor = orm.relationship(
        model.Vendor,
        doc="""
        Reference to the vendor associated with the invoice, or
        ``None``.
        """,
        backref=orm.backref(
            'dtail_qbo_invoices',
            cascade='all'))

    quickbooks_vendor_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks name for the invoice vendor.
    """)

    quickbooks_vendor_terms = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks terms for the invoice vendor.
    """)

    quickbooks_bank_account = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks bank account for the invoice vendor.
    """)

    quickbooks_export_template = sa.Column(sa.String(length=100), nullable=True, doc="""
    Name of the Quickbooks export template to use for this invoice.
    """)

    status_code = sa.Column(sa.Integer(), nullable=False, doc="""
    Status code for the invoice; indicates whether it's exportable etc.
    """)

    status_text = sa.Column(sa.String(length=255), nullable=True, doc="""
    Extra text relating to the invoice status, if applicable.
    """)

    ##################################################
    # other columns
    ##################################################

    deleted = sa.Column(sa.DateTime(), nullable=True, doc="""
    Timestamp when the invoice was marked as deleted, or ``None``.
    """)

    deleted_by_uuid = sa.Column(sa.String(length=32), nullable=True)
    deleted_by = orm.relationship(
        model.User,
        primaryjoin='User.uuid == QuickbooksExportableInvoice.deleted_by_uuid',
        doc="""
        Reference to the :class:`rattail:~rattail.db.model.User`
        instance who marked the invoice as deleted, or ``None``.
        """)

    exported = sa.Column(sa.DateTime(), nullable=True, doc="""
    Timestamp when the invoice was exported, or ``None``.
    """)

    exported_by_uuid = sa.Column(sa.String(length=32), nullable=True)
    exported_by = orm.relationship(
        model.User,
        primaryjoin='User.uuid == QuickbooksExportableInvoice.exported_by_uuid',
        doc="""
        Reference to the :class:`rattail:~rattail.db.model.User`
        instance who exported the invoice, or ``None``.
        """)

    def __str__(self):
        return "{}, {}, {} (trans. {})".format(self.store_id,
                                               self.vendor_id,
                                               self.invoice_number,
                                               self.txn_id)

    def add_distribution(self, **kwargs):
        dist = QuickbooksExportableInvoiceDistribution(**kwargs)
        if not dist.status_code:
            dist.status_code = dist.STATUS_NOT_YET_REFRESHED
        self.distributions.append(dist)


class QuickbooksExportableInvoiceDistribution(model.Base):
    """
    Represents a "distribution" for a department, within the context
    of a vendor invoice which is to be exported to Quickbooks.
    """
    __tablename__ = 'quickbooks_exportable_invoice_dist'
    __table_args__ = (
        sa.ForeignKeyConstraint(['invoice_uuid'], ['quickbooks_exportable_invoice.uuid'],
                                name='quickbooks_exportable_invoice_dist_fk_invoice'),
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'],
                                name='quickbooks_exportable_invoice_dist_fk_department'),
    )

    STATUS_NOT_YET_REFRESHED             = 1
    STATUS_EXPORTABLE                    = 2
    STATUS_DEPT_NOT_FOUND                = 3
    STATUS_DEPT_IGNORED                  = 4
    STATUS_DEPT_BAD_INFO                 = 5
    STATUS_EXPORTED                      = 6

    STATUS = OrderedDict([
        (STATUS_NOT_YET_REFRESHED,      "data not yet refreshed"),
        (STATUS_EXPORTABLE,             "exportable"),
        (STATUS_DEPT_NOT_FOUND,         "department not found"),
        (STATUS_DEPT_IGNORED,           "department ignored"),
        (STATUS_DEPT_BAD_INFO,          "department info is invalid"),
        (STATUS_EXPORTED,               "exported"),
    ])

    uuid = model.uuid_column()

    invoice_uuid = sa.Column(sa.String(length=32), nullable=False)
    invoice = orm.relationship(
        QuickbooksExportableInvoice,
        doc="""
        Reference to the parent invoice.
        """,
        backref=orm.backref(
            'distributions',
            cascade='all',
            doc="""
            Sequence of
            :class:`QuickbooksExportableInvoiceDistribution` instances
            which belong to the invoice.
            """))

    ##################################################
    # columns whose values come from source data
    ##################################################

    department_id = sa.Column(sa.Integer(), nullable=False, doc="""
    Department ID for the distribution, per source data.
    """)

    source_amount = sa.Column(sa.Numeric(precision=8, scale=2), nullable=False, doc="""
    Dollar amount for the distribution, per source data.
    """)

    ##################################################
    # columns whose values come from data refresh
    ##################################################

    department_uuid = sa.Column(sa.String(length=32), nullable=True)
    department = orm.relationship(
        model.Department,
        doc="""
        Reference to the :class:`rattail:~rattail.db.model.Department`
        instance associated with the distribution, or ``None``.
        """)

    quickbooks_expense_account = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks expense account for the department.
    """)

    quickbooks_expense_class = sa.Column(sa.String(length=100), nullable=True, doc="""
    Quickbooks expense class for the department.
    """)

    calculated_percent = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Percentage of the invoice total which should be considered
    attributable to the current distribution (department).  This is
    calculated after taking "ignored" departments into consideration,
    etc.
    """)

    calculated_amount = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Dollar amount for the distribution, per business logic.
    """)

    status_code = sa.Column(sa.Integer(), nullable=False, doc="""
    Status code for the distribution; indicates whether it's
    exportable etc.
    """)

    status_text = sa.Column(sa.String(length=255), nullable=True, doc="""
    Extra text relating to the distribution, if applicable.
    """)


class QuickbooksInvoiceExport(model.ExportMixin, model.Base):
    """
    Invoice export file, for *consumption* by Quickbooks.
    """
    __tablename__ = 'quickbooks_invoice_export'

    filename = filename_column(nullable=True, doc="""
    Filename for the export.
    """)
