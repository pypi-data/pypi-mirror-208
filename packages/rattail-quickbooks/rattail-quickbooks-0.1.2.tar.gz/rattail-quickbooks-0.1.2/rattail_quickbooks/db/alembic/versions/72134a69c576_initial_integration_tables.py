# -*- coding: utf-8; -*-
"""initial integration tables

Revision ID: 72134a69c576
Revises: dc28b97c33ff
Create Date: 2022-12-08 15:19:54.448794

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '72134a69c576'
down_revision = None
branch_labels = ('rattail_quickbooks',)
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # quickbooks_store
    op.create_table('quickbooks_store',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('quickbooks_location', sa.String(length=100), nullable=True),
                    sa.ForeignKeyConstraint(['uuid'], ['store.uuid'], name='quickbooks_store_fk_store'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('quickbooks_store_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('quickbooks_location', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_quickbooks_store_version_end_transaction_id'), 'quickbooks_store_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_quickbooks_store_version_operation_type'), 'quickbooks_store_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_quickbooks_store_version_transaction_id'), 'quickbooks_store_version', ['transaction_id'], unique=False)

    # quickbooks_department
    op.create_table('quickbooks_department',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('quickbooks_expense_account', sa.String(length=100), nullable=True),
                    sa.Column('quickbooks_expense_class', sa.String(length=100), nullable=True),
                    sa.ForeignKeyConstraint(['uuid'], ['department.uuid'], name='quickbooks_department_fk_department'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('quickbooks_department_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('quickbooks_expense_account', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('quickbooks_expense_class', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_quickbooks_department_version_end_transaction_id'), 'quickbooks_department_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_quickbooks_department_version_operation_type'), 'quickbooks_department_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_quickbooks_department_version_transaction_id'), 'quickbooks_department_version', ['transaction_id'], unique=False)

    # quickbooks_vendor
    op.create_table('quickbooks_vendor',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('quickbooks_name', sa.String(length=100), nullable=True),
                    sa.Column('quickbooks_bank_account', sa.String(length=100), nullable=True),
                    sa.Column('quickbooks_terms', sa.String(length=100), nullable=True),
                    sa.ForeignKeyConstraint(['uuid'], ['vendor.uuid'], name='quickbooks_vendor_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('quickbooks_vendor_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('quickbooks_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('quickbooks_bank_account', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('quickbooks_terms', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_quickbooks_vendor_version_end_transaction_id'), 'quickbooks_vendor_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_quickbooks_vendor_version_operation_type'), 'quickbooks_vendor_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_quickbooks_vendor_version_transaction_id'), 'quickbooks_vendor_version', ['transaction_id'], unique=False)

    # quickbooks_exportable_invoice
    op.create_table('quickbooks_exportable_invoice',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('store_id', sa.String(length=4), nullable=True),
                    sa.Column('vendor_id', sa.String(length=14), nullable=True),
                    sa.Column('txn_id', sa.String(length=20), nullable=True),
                    sa.Column('invoice_number', sa.String(length=20), nullable=True),
                    sa.Column('invoice_date', sa.Date(), nullable=True),
                    sa.Column('invoice_total', sa.Numeric(precision=8, scale=2), nullable=False),
                    sa.Column('store_uuid', sa.String(length=32), nullable=True),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=True),
                    sa.Column('quickbooks_vendor_name', sa.String(length=100), nullable=True),
                    sa.Column('quickbooks_vendor_terms', sa.String(length=100), nullable=True),
                    sa.Column('quickbooks_bank_account', sa.String(length=100), nullable=True),
                    sa.Column('quickbooks_export_template', sa.String(length=100), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=False),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('deleted', sa.DateTime(), nullable=True),
                    sa.Column('deleted_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('exported', sa.DateTime(), nullable=True),
                    sa.Column('exported_by_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['deleted_by_uuid'], ['user.uuid'], name='quickbooks_exportable_invoice_fk_deleted_by'),
                    sa.ForeignKeyConstraint(['exported_by_uuid'], ['user.uuid'], name='quickbooks_exportable_invoice_fk_exported_by'),
                    sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='quickbooks_exportable_invoice_fk_store'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'], name='quickbooks_exportable_invoice_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('quickbooks_exportable_invoice_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('store_id', sa.String(length=4), autoincrement=False, nullable=True),
                    sa.Column('vendor_id', sa.String(length=14), autoincrement=False, nullable=True),
                    sa.Column('txn_id', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('invoice_number', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('invoice_date', sa.Date(), autoincrement=False, nullable=True),
                    sa.Column('invoice_total', sa.Numeric(precision=8, scale=2), autoincrement=False, nullable=True),
                    sa.Column('store_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('vendor_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('quickbooks_vendor_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('quickbooks_vendor_terms', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('quickbooks_bank_account', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('quickbooks_export_template', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('status_code', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('status_text', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('deleted', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('deleted_by_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('exported', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('exported_by_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_quickbooks_exportable_invoice_version_end_transaction_id'), 'quickbooks_exportable_invoice_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_quickbooks_exportable_invoice_version_operation_type'), 'quickbooks_exportable_invoice_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_quickbooks_exportable_invoice_version_transaction_id'), 'quickbooks_exportable_invoice_version', ['transaction_id'], unique=False)

    # quickbooks_exportable_invoice_dist
    op.create_table('quickbooks_exportable_invoice_dist',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('invoice_uuid', sa.String(length=32), nullable=False),
                    sa.Column('department_id', sa.Integer(), nullable=False),
                    sa.Column('source_amount', sa.Numeric(precision=8, scale=2), nullable=False),
                    sa.Column('department_uuid', sa.String(length=32), nullable=True),
                    sa.Column('quickbooks_expense_account', sa.String(length=100), nullable=True),
                    sa.Column('quickbooks_expense_class', sa.String(length=100), nullable=True),
                    sa.Column('calculated_percent', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('calculated_amount', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='quickbooks_exportable_invoice_dist_fk_department'),
                    sa.ForeignKeyConstraint(['invoice_uuid'], ['quickbooks_exportable_invoice.uuid'], name='quickbooks_exportable_invoice_dist_fk_invoice'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # quickbooks_invoice_export
    op.create_table('quickbooks_invoice_export',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('record_count', sa.Integer(), nullable=True),
                    sa.Column('filename', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='quickbooks_invoice_export_fk_created_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # quickbooks_invoice_export
    op.drop_table('quickbooks_invoice_export')

    # quickbooks_exportable_invoice_dist
    op.drop_table('quickbooks_exportable_invoice_dist')

    # quickbooks_exportable_invoice_dist
    op.drop_index(op.f('ix_quickbooks_exportable_invoice_version_transaction_id'), table_name='quickbooks_exportable_invoice_version')
    op.drop_index(op.f('ix_quickbooks_exportable_invoice_version_operation_type'), table_name='quickbooks_exportable_invoice_version')
    op.drop_index(op.f('ix_quickbooks_exportable_invoice_version_end_transaction_id'), table_name='quickbooks_exportable_invoice_version')
    op.drop_table('quickbooks_exportable_invoice_version')
    op.drop_table('quickbooks_exportable_invoice')

    # quickbooks_vendor
    op.drop_index(op.f('ix_quickbooks_vendor_version_transaction_id'), table_name='quickbooks_vendor_version')
    op.drop_index(op.f('ix_quickbooks_vendor_version_operation_type'), table_name='quickbooks_vendor_version')
    op.drop_index(op.f('ix_quickbooks_vendor_version_end_transaction_id'), table_name='quickbooks_vendor_version')
    op.drop_table('quickbooks_vendor_version')
    op.drop_table('quickbooks_vendor')

    # quickbooks_department
    op.drop_index(op.f('ix_quickbooks_department_version_transaction_id'), table_name='quickbooks_department_version')
    op.drop_index(op.f('ix_quickbooks_department_version_operation_type'), table_name='quickbooks_department_version')
    op.drop_index(op.f('ix_quickbooks_department_version_end_transaction_id'), table_name='quickbooks_department_version')
    op.drop_table('quickbooks_department_version')
    op.drop_table('quickbooks_department')

    # quickbooks_store
    op.drop_index(op.f('ix_quickbooks_store_version_transaction_id'), table_name='quickbooks_store_version')
    op.drop_index(op.f('ix_quickbooks_store_version_operation_type'), table_name='quickbooks_store_version')
    op.drop_index(op.f('ix_quickbooks_store_version_end_transaction_id'), table_name='quickbooks_store_version')
    op.drop_table('quickbooks_store_version')
    op.drop_table('quickbooks_store')
