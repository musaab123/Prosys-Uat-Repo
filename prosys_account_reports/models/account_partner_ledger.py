# * coding: utf8 *


from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from datetime import timedelta


class AccountPartnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    filter_salesteam = True

    @api.model
    def _get_options_domain(self, options, date_scope):
        domain = super(AccountPartnerLedger, self)._get_options_domain(options, date_scope)
        if options.get('salesteam') and options.get('salesteams'):
            salesteams = [int(salesteam) for salesteam in options['salesteams']]
            domain.append(('team_id', 'in', salesteams))
        return domain
