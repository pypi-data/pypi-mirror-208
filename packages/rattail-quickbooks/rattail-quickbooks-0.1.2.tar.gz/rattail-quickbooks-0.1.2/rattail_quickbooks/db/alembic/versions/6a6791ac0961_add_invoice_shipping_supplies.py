# -*- coding: utf-8; -*-
"""add invoice shipping, supplies

Revision ID: 6a6791ac0961
Revises: 72134a69c576
Create Date: 2022-12-21 19:06:31.833258

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '6a6791ac0961'
down_revision = '72134a69c576'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # quickbooks_exportable_invoice
    op.add_column('quickbooks_exportable_invoice', sa.Column('shipping_amount', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column('quickbooks_exportable_invoice', sa.Column('supplies_amount', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column('quickbooks_exportable_invoice_version', sa.Column('shipping_amount', sa.Numeric(precision=8, scale=2), autoincrement=False, nullable=True))
    op.add_column('quickbooks_exportable_invoice_version', sa.Column('supplies_amount', sa.Numeric(precision=8, scale=2), autoincrement=False, nullable=True))

    # quickbooks_exportable_invoice_dist
    op.add_column('quickbooks_exportable_invoice_dist', sa.Column('status_text', sa.String(length=255), nullable=True))


def downgrade():

    # quickbooks_exportable_invoice_dist
    op.drop_column('quickbooks_exportable_invoice_dist', 'status_text')

    # quickbooks_exportable_invoice
    op.drop_column('quickbooks_exportable_invoice_version', 'supplies_amount')
    op.drop_column('quickbooks_exportable_invoice_version', 'shipping_amount')
    op.drop_column('quickbooks_exportable_invoice', 'supplies_amount')
    op.drop_column('quickbooks_exportable_invoice', 'shipping_amount')
