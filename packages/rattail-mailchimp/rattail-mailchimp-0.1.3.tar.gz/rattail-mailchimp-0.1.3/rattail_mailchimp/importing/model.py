# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
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
Rattail/MailChimp model importers
"""

from rattail.importing.model import ToRattail
from rattail_mailchimp.db import model


##############################
# custom models
##############################

class MailChimpListImporter(ToRattail):
    """
    Importer for MailChimpList data
    """
    model_class = model.MailChimpList


class MailChimpListMemberImporter(ToRattail):
    """
    Importer for MailChimpListMember data
    """
    model_class = model.MailChimpListMember

    @property
    def supported_fields(self):
        return self.simple_fields + [
            'list_id',
        ]

    def setup(self):
        super(MailChimpListMemberImporter, self).setup()

        if 'list_id' in self.fields:
            model = self.model
            self.mailchimp_lists = self.cache_model(model.MailChimpList,
                                                    key='id')

    def get_mailchimp_list(self, list_id):
        if hasattr(self, 'mailchimp_lists'):
            return self.mailchimp_lists.get(list_id)

        model = self.model
        return self.session.query(model.MailChimpList)\
                           .filter(model.MailChimpList.id == list_id)\
                           .first()

    def normalize_local_object(self, member):
        data = super(MailChimpListMemberImporter, self).normalize_local_object(member)

        if 'list_id' in self.fields:
            data['list_id'] = member.list.id if member.list else None

        return data

    def update_object(self, member, data, local_data=None):
        member = super(MailChimpListMemberImporter, self).update_object(member, data, local_data)

        if 'list_id' in self.fields:
            list_id = data['list_id']
            if list_id:
                mclist = self.get_mailchimp_list(list_id)
                assert mclist
                member.list = mclist                    
            elif member.list:
                member.list = None

        return member
