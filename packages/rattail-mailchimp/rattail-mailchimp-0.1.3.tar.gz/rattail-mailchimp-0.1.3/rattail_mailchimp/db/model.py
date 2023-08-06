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
Database schema extensions for Mailchimp integration
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model


class MailChimpList(model.Base):
    """
    List record cache for MailChimp.
    """
    __tablename__ = 'mailchimp_list'
    model_title = "MailChimp List"

    uuid = model.uuid_column()

    id = sa.Column(sa.String(length=100), nullable=True)

    name = sa.Column(sa.String(length=100), nullable=True)

    date_created = sa.Column(sa.DateTime(), nullable=True)

    members = orm.relationship('MailChimpListMember',
                               back_populates='list',
                               # nb. this is to satisfy SA 2.0
                               cascade_backrefs=False)

    def __str__(self):
        return self.name or ""


class MailChimpListMember(model.Base):
    """
    ListMember record cache for MailChimp.
    """
    __tablename__ = 'mailchimp_list_member'
    __table_args__ = (
        sa.ForeignKeyConstraint(['list_uuid'], ['mailchimp_list.uuid'], 
                                name='mailchimp_list_member_fk_list'),
    )

    uuid = model.uuid_column()

    list_uuid = sa.Column(sa.String(length=32), nullable=False)
    list = orm.relationship(MailChimpList,
                            back_populates='members')

    id = sa.Column(sa.String(length=32), nullable=True)

    email_address = sa.Column(sa.String(length=255), nullable=True)

    contact_id = sa.Column(sa.String(length=50), nullable=True)

    full_name = sa.Column(sa.String(length=100), nullable=True)

    email_type = sa.Column(sa.String(length=10), nullable=True)

    status = sa.Column(sa.String(length=20), nullable=True)

    unsubscribe_reason = sa.Column(sa.Text(), nullable=True)

    last_changed = sa.Column(sa.DateTime(), nullable=True)

    source = sa.Column(sa.String(length=255), nullable=True)

    def __str__(self):
        return self.email_address or ""
