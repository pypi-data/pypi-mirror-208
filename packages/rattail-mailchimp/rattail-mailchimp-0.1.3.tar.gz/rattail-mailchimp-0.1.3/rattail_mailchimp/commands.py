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
Rattail Commands for MailChimp integration
"""

from rattail import commands
from rattail.util import load_object


class ImportMailChimp(commands.ImportSubcommand):
    """
    Import data to Rattail, from MailChimp API
    """
    name = 'import-mailchimp'
    description = __doc__.strip()
    default_handler_spec = 'rattail_mailchimp.importing.mailchimp:FromMailChimpToRattail'

    def get_handler_factory(self, **kwargs):
        if self.config:
            spec = self.config.get('rattail.importing', 'mailchimp.handler',
                                   default=self.default_handler_spec)
        else:
            # just use default, for sake of cmd line help
            spec = self.default_handler_spec
        return load_object(spec)
