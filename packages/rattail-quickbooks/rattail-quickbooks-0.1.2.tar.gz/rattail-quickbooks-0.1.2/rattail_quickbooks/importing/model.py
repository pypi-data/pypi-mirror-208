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
rattail-quickbooks model importers
"""

from rattail import importing


##############################
# core importer overrides
##############################

class StoreImporter(importing.model.StoreImporter):

    extension_attr = '_quickbooks'
    extension_fields = [
        'quickbooks_location',
    ]


class DepartmentImporter(importing.model.DepartmentImporter):

    extension_attr = '_quickbooks'
    extension_fields = [
        'quickbooks_expense_account',
        'quickbooks_expense_class',
    ]


class VendorImporter(importing.model.VendorImporter):

    extension_attr = '_quickbooks'
    extension_fields = [
        'quickbooks_name',
        'quickbooks_bank_account',
        'quickbooks_terms',
    ]


##############################
# custom models
##############################

class QuickbooksExportableInvoiceImporter(importing.model.ToRattail):

    def get_model_class(self):
        return self.model.QuickbooksExportableInvoice

    def cache_query(self):
        query = super(QuickbooksExportableInvoiceImporter, self).cache_query()
        model = self.model
        # TODO: possibly should filter this way only if config says so?
        if self.start_date:
            query = query.filter(model.QuickbooksExportableInvoice.invoice_date >= self.start_date)
        if self.end_date:
            query = query.filter(model.QuickbooksExportableInvoice.invoice_date <= self.end_date)
        return query
