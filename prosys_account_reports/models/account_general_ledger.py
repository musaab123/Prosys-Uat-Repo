# * coding: utf8 *


from odoo import models, fields, api, _
from odoo.tools.misc import format_date
from datetime import timedelta
from odoo.tools import float_is_zero


class report_account_general_ledger(models.AbstractModel):
    _inherit = "account.general.ledger.report.handler"

    filter_salesteam = True

    @api.model
    def _get_options_domain(self, options, date_scope):
        domain = super(report_account_general_ledger,
                       self)._get_options_domain(options, date_scope)
        if options.get('salesteam') and options.get('salesteams'):
            salesteams = [int(salesteam) for salesteam in options['salesteams']]
            domain.append(('team_id', 'in', salesteams))
        return domain
