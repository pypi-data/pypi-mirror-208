# -*- coding: utf-8; -*-
"""initial tables

Revision ID: 805181d09df7
Revises: 8856f697902d
Create Date: 2021-11-07 21:17:31.196005

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '805181d09df7'
down_revision = None
branch_labels = ('rattail_mailchimp',)
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # mailchimp_list
    op.create_table('mailchimp_list',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.String(length=100), nullable=True),
                    sa.Column('name', sa.String(length=100), nullable=True),
                    sa.Column('date_created', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # mailchimp_list_member
    op.create_table('mailchimp_list_member',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('list_uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.String(length=32), nullable=True),
                    sa.Column('email_address', sa.String(length=255), nullable=True),
                    sa.Column('contact_id', sa.String(length=50), nullable=True),
                    sa.Column('full_name', sa.String(length=100), nullable=True),
                    sa.Column('email_type', sa.String(length=10), nullable=True),
                    sa.Column('status', sa.String(length=20), nullable=True),
                    sa.Column('unsubscribe_reason', sa.Text(), nullable=True),
                    sa.Column('last_changed', sa.DateTime(), nullable=True),
                    sa.Column('source', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['list_uuid'], ['mailchimp_list.uuid'], name='mailchimp_list_member_fk_list'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # mailchimp_list*
    op.drop_table('mailchimp_list_member')
    op.drop_table('mailchimp_list')
