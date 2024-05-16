# * coding: utf8 *


from odoo import models, fields, api, _


class AccountReport(models.Model):
    _inherit = 'account.report'

    filter_salesteam = fields.Boolean(
        string="Sales Teams",
        compute=lambda x: x._compute_report_option_filter('filter_salesteam'), readonly=False, store=True, depends=['root_report_id'],
    )

    @api.model
    def _init_options_salesteam(self, options, previous_options=None):
        query = "UPDATE account_move_line SET team_id=(SELECT team_id from account_move where id=account_move_line.move_id) WHERE account_move_line.team_id is NULL;"
        self.env.cr.execute(query)
        options['salesteam'] = True
        res_salesteam_obj = self.env['crm.team']
        options['salesteams'] = previous_options and previous_options.get('salesteams') or [
        ]
        
        team_ids = [int(salesteam) for salesteam in options['salesteams']]
        selected_team_ids = team_ids and res_salesteam_obj.browse(
            team_ids) or res_salesteam_obj
        options['selected_team_ids'] = selected_team_ids.mapped('name')

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('salesteams'):
            ctx['team_ids'] = self.env['crm.team'].browse(
                [int(salesteam) for salesteam in options['salesteams']]).ids
        return ctx

    def get_report_informations(self, options):
        options = self._get_options(options)
        if options.get('salesteam'):
            options['selected_team_ids'] = [self.env['crm.team'].browse(
                int(salesteam)).name for salesteam in options['salesteams']]
        return super(AccountReport, self).get_report_informations(options)

    @api.model
    def _get_options_domain(self, options, date_scope):
        domain = super(AccountReport, self)._get_options_domain(options, date_scope)
        if options.get('salesteam') and options.get('salesteams'):
            salesteams = [int(salesteam) for salesteam in options['salesteams']]
            domain.append(('team_id', 'in', salesteams))
        return domain