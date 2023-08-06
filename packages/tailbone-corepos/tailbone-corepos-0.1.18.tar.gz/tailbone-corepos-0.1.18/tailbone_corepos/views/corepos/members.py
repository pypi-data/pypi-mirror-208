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
CORE-POS member views
"""

from corepos.db.office_op import model as corepos

from rattail_corepos.config import core_office_customer_account_url

from webhelpers2.html import HTML, tags

from .master import CoreOfficeMasterView


class MemberTypeView(CoreOfficeMasterView):
    """
    Master view for member types
    """
    model_class = corepos.MemberType
    model_title = "CORE-POS Member Type"
    url_prefix = '/core-pos/member-types'
    route_prefix = 'corepos.member_types'

    labels = {
        'id': "ID",
        'ssi': "SSI",
    }

    def configure_grid(self, g):
        super(MemberTypeView, self).configure_grid(g)

        g.set_link('id')
        g.set_link('description')


class MemberView(CoreOfficeMasterView):
    """
    Master view for members
    """
    model_class = corepos.MemberInfo
    model_title = "CORE-POS Member (Legacy)"
    model_title_plural = "CORE-POS Members (Legacy)"
    url_prefix = '/core-pos/members'
    route_prefix = 'corepos.members'

    labels = {
        'card_number': "Card No.",
        'email2': "Email 2",
        'ads_ok': "Ads OK",
    }

    grid_columns = [
        'card_number',
        'first_name',
        'last_name',
        'street',
        'city',
        'state',
        'zip',
        'phone',
        'email',
    ]

    form_fields = [
        'card_number',
        'first_name',
        'last_name',
        'other_first_name',
        'other_last_name',
        'customers',
        'street',
        'city',
        'state',
        'zip',
        'phone',
        'email',
        'email2',
        'ads_ok',
        'dates',
        'barcodes',
        'suspension',
    ]

    def configure_grid(self, g):
        super(MemberView, self).configure_grid(g)

        g.set_sort_defaults('card_number')

        g.filters['card_number'].default_active = True
        g.filters['card_number'].default_verb = 'equal'

        g.set_link('card_number')
        g.set_link('first_name')
        g.set_link('last_name')

    def configure_form(self, f):
        super(MemberView, self).configure_form(f)

        f.set_renderer('dates', self.render_member_dates)

        f.set_renderer('barcodes', self.render_barcodes)

        f.set_readonly('customers')
        f.set_renderer('customers', self.render_customers)

        f.set_renderer('suspension', self.render_suspension)

    def render_member_dates(self, member, field):
        if not member.dates:
            return ""

        items = []
        for dates in member.dates:
            items.append(HTML.tag('li', c=str(dates)))
        return HTML.tag('ul', c=items)

    def render_barcodes(self, member, field):
        barcodes = member.barcodes
        if not barcodes:
            return

        items = []
        for barcode in barcodes:
            if barcode.upc:
                text = barcode.upc
            elif barcode.upc is None:
                text = "(null)"
            else:
                text = "(empty string)"
            items.append(HTML.tag('li', c=[text]))
        return HTML.tag('ul', c=items)

    def render_customers(self, member, field):
        customers = member.customers
        if not customers:
            return

        items = []
        for customer in customers:
            text = str(customer)
            url = self.request.route_url('corepos.customers.view', id=customer.id)
            link = tags.link_to(text, url)
            items.append(HTML.tag('li', c=[link]))
        return HTML.tag('ul', c=items)

    def render_suspension(self, member, field):
        suspension = member.suspension
        if not suspension:
            return

        text = str(suspension)
        url = self.request.route_url('corepos.suspensions.view',
                                     card_number=suspension.card_number)
        return tags.link_to(text, url)

    def core_office_object_url(self, office_url, member):
        return core_office_customer_account_url(self.rattail_config,
                                                member.card_number,
                                                office_url=office_url)


def defaults(config, **kwargs):
    base = globals()

    MemberTypeView = kwargs.get('MemberTypeView', base['MemberTypeView'])
    MemberTypeView.defaults(config)

    MemberView = kwargs.get('MemberView', base['MemberView'])
    MemberView.defaults(config)


def includeme(config):
    defaults(config)
