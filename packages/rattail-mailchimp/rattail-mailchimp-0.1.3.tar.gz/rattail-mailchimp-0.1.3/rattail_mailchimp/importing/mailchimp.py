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
MailChimp -> Rattail "cache" data import
"""

import datetime
from collections import OrderedDict

from mailchimp3 import MailChimp

from rattail import importing
from rattail.time import localtime, make_utc
from rattail_mailchimp import importing as mailchimp_importing


class FromMailChimpToRattail(importing.ToRattailHandler):
    """
    Handler for MailChimp -> Rattail cache import
    """
    host_title = "MailChimp"
    
    def get_importers(self):
        importers = OrderedDict()
        importers['MailChimpList'] = MailChimpListImporter
        importers['MailChimpListMember'] = MailChimpListMemberImporter
        return importers


class FromMailChimp(importing.Importer):
    """
    Base class for importers coming from MailChimp
    """

    def setup(self):
        super(FromMailChimp, self).setup()

        self.api_key = self.config.require('mailchimp', 'api_key')
        self.mailchimp = MailChimp(self.api_key)

    def mailchimp_datetime(self, value):
        if value.endswith('+00:00'):
            # TODO: for some reason the '%z' format did not work on a
            # python 3.5 system, so here we try to ignore the
            # issue..since we clearly have a UTC value
            value = value[:-6]
            dt = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
            dt = localtime(self.config, dt, from_utc=True)
        else:
            dt = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
            dt = localtime(self.config, dt)
        return dt


class MailChimpListImporter(FromMailChimp, mailchimp_importing.model.MailChimpListImporter):
    """
    List importer for MailChimp -> Rattail

    https://github.com/VingtCinq/python-mailchimp#lists-1
    https://mailchimp.com/developer/marketing/api/lists/get-lists-info/
    """
    key = 'id'
    supported_fields = [
        'id',
        'name',
        'date_created',
    ]

    def get_host_objects(self):
        result = self.mailchimp.lists.all(get_all=True)
        return result['lists']

    def normalize_host_object(self, mclist):
        date_created = self.mailchimp_datetime(mclist['date_created'])
        return {
            'id': mclist['id'],
            'name': mclist['name'],
            'date_created': make_utc(date_created),
        }


class MailChimpListMemberImporter(FromMailChimp, mailchimp_importing.model.MailChimpListMemberImporter):
    """
    List importer for MailChimp -> Rattail

    https://github.com/VingtCinq/python-mailchimp#list-members
    https://mailchimp.com/developer/marketing/api/list-members/list-members-info/
    """
    key = ('list_id', 'contact_id')
    supported_fields = [
        'list_id',
        'id',
        'email_address',
        'contact_id',
        'full_name',
        'email_type',
        'status',
        # 'unsubscribe_reason',
        'last_changed',
        'source',
    ]

    def get_host_objects(self):
        model = self.model
        objects = []
        mclists = self.session.query(model.MailChimpList).all()
        for mclist in mclists:
            objects.extend(self.get_all_members(mclist.id))
        return objects

    def get_all_members(self, list_id):
        members = []
        # cf. https://mailchimp.com/developer/marketing/api/list-members/list-members-info/
        result = self.mailchimp.lists.members.all(list_id, get_all=True,

                                                  # TODO: maybe should try this instead of
                                                  # the default which seems to be 500
                                                  # count=1000

                                                  # TODO: this testing chunk left here for
                                                  # reference; it can be handy to filter
                                                  # results etc. for test runs
                                                  # count=500,
                                                  # # since_last_changed=datetime.date(2023, 1, 1),
                                                  # sort_field='last_changed',
                                                  # sort_dir='DESC',
        )
        members.extend(result['members'])
        return members

    def normalize_host_object(self, member):
        last_changed = self.mailchimp_datetime(member['last_changed'])
        return {
            'list_id': member['list_id'],
            'id': member['id'],
            'email_address': member['email_address'],
            'contact_id': member['contact_id'],
            'full_name': member['full_name'],
            'email_type': member['email_type'],
            'status': member['status'],
            # TODO: this API endpoint does not appear to include this field?
            # 'unsubscribe_reason': member.get('unsubscribe_reason'),
            'last_changed': make_utc(last_changed),
            'source': member['source'],
        }
