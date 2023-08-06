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
Vendor views
"""

from rattail_corepos.config import core_office_url

from tailbone.views import ViewSupplement


class VendorViewSupplement(ViewSupplement):
    """
    Vendor view supplement for CORE integration
    """
    route_prefix = 'vendors'

    labels = {
        'corepos_id': "CORE-POS ID",
    }

    def get_grid_query(self, query):
        model = self.model
        return query.outerjoin(model.CoreVendor)

    def configure_grid(self, g):
        model = self.model
        g.set_filter('corepos_id', model.CoreVendor.corepos_id)

    def configure_form(self, f):
        f.append('corepos_id')

    def get_version_child_classes(self):
        model = self.model
        return [model.CoreVendor]

    def get_xref_buttons(self, vendor):
        url = core_office_url(self.rattail_config)
        if url:
            url = '{}/item/vendors/VendorIndexPage.php?vid={}'.format(
                url, vendor.corepos_id)
            return [{'url': url, 'text': "View in CORE Office"}]


def includeme(config):
    VendorViewSupplement.defaults(config)
