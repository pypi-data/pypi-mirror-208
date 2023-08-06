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
Common menus for CORE-POS
"""

from rattail_corepos.config import core_office_url


def make_corepos_menu(request):

    corepos_menu = {
        'title': "CORE-POS",
        'type': 'menu',
        'items': [
            {
                'title': "People",
                'type': 'menu',
                'items': [
                    {
                        'title': "Customers (Legacy)",
                        'route': 'corepos.customers',
                        'perm': 'corepos.customers.list',
                    },
                    {
                        'title': "Members (Legacy)",
                        'route': 'corepos.members',
                        'perm': 'corepos.members.list',
                    },
                    {
                        'title': "Suspensions",
                        'route': 'corepos.suspensions',
                        'perm': 'corepos.suspensions.list',
                    },
                    {
                        'title': "Member Types",
                        'route': 'corepos.member_types',
                        'perm': 'corepos.member_types.list',
                    },
                    {
                        'title': "Employees",
                        'route': 'corepos.employees',
                        'perm': 'corepos.employees.list',
                    },
                    {
                        'title': "Users",
                        'route': 'corepos.users',
                        'perm': 'corepos.users.list',
                    },
                    {
                        'title': "User Groups",
                        'route': 'corepos.user_groups',
                        'perm': 'corepos.user_groups.list',
                    },
                ],
            },
            {
                'title': "Products",
                'type': 'menu',
                'items': [
                    {
                        'title': "Products",
                        'route': 'corepos.products',
                        'perm': 'corepos.products.list',
                    },
                    {
                        'title': "Product Flags",
                        'route': 'corepos.product_flags',
                        'perm': 'corepos.product_flags.list',
                    },
                    {
                        'title': "Like Codes",
                        'route': 'corepos.like_codes',
                        'perm': 'corepos.like_codes.list',
                    },
                    {
                        'title': "Scale Items",
                        'route': 'corepos.scale_items',
                        'perm': 'corepos.scale_items.list',
                    },
                    {
                        'title': "Origins",
                        'route': 'corepos.origins',
                        'perm': 'corepos.origins.list',
                    },
                    {'type': 'sep'},
                    {
                        'title': "Super Departments",
                        'route': 'corepos.super_departments',
                        'perm': 'corepos.super_departments.list',
                    },
                    {
                        'title': "Departments",
                        'route': 'corepos.departments',
                        'perm': 'corepos.departments.list',
                    },
                    {
                        'title': "Subdepartments",
                        'route': 'corepos.subdepartments',
                        'perm': 'corepos.subdepartments.list',
                    },
                    {'type': 'sep'},
                    {
                        'title': "Batches",
                        'route': 'corepos.batches',
                        'perm': 'corepos.batches.list',
                    },
                    {
                        'title': "Batch Types",
                        'route': 'corepos.batch_types',
                        'perm': 'corepos.batch_types.list',
                    },
                ],
            },
            {
                'title': "Vendors",
                'type': 'menu',
                'items': [
                    {
                        'title': "Vendors",
                        'route': 'corepos.vendors',
                        'perm': 'corepos.vendors.list',
                    },
                    {
                        'title': "Vendor Items",
                        'route': 'corepos.vendor_items',
                        'perm': 'corepos.vendor_items.list',
                    },
                    {
                        'title': "Purchase Orders",
                        'route': 'corepos.purchase_orders',
                        'perm': 'corepos.purchase_orders.list',
                    },
                ],
            },
            {
                'title': "Transactions",
                'type': 'menu',
                'items': [
                    {
                        'title': "Tax Rates",
                        'route': 'corepos.taxrates',
                        'perm': 'corepos.taxrates.list',
                    },
                    {
                        'title': "House Coupons",
                        'route': 'corepos.house_coupons',
                        'perm': 'corepos.house_coupons.list',
                    },
                    {
                        'title': "Transaction Details",
                        'route': 'corepos.transaction_details',
                        'perm': 'corepos.transaction_details.list',
                    },
                ],
            },
            {
                'title': "Misc.",
                'type': 'menu',
                'items': [
                    {
                        'title': "Stores",
                        'route': 'corepos.stores',
                        'perm': 'corepos.stores.list',
                    },
                    {
                        'title': "Parameters",
                        'route': 'corepos.parameters',
                        'perm': 'corepos.parameters.list',
                    },
                    {
                        'title': "Table Sync Rules",
                        'route': 'corepos.table_sync_rules',
                        'perm': 'corepos.table_sync_rules.list',
                    },
                ],
            },
        ],
    }

    office_url = core_office_url(request.rattail_config)
    if office_url:
        corepos_menu['items'].insert(
            0, {
                'title': "Go to CORE Office",
                'url': '{}/'.format(office_url),
                'target': '_blank',
            })
        corepos_menu['items'].insert(
            1, {'type': 'sep'})

    return corepos_menu
