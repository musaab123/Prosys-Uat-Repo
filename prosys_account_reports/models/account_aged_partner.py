from odoo import models, api, fields, _
from odoo.tools.misc import format_date

from dateutil.relativedelta import relativedelta
from itertools import chain


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self,vals):
        result = super().write(vals)
        for record in self:
            record.line_ids._add_sales_team(team_id=vals.get('team_id'))
        return result

    @api.model
    def create(self,vals):
        result = super().create(vals)
        for record in result:
            record.line_ids._add_sales_team(team_id=vals.get('team_id'))
        return result

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    team_id = fields.Many2one('crm.team')

    """
        UPDATE account_move_line 
                            SET team_id=
                            (SELECT team_id from account_move WHERE id=account_move_line.move_id)
        WHERE move_id=account_move_line.move_id;
    """

    def _add_sales_team(self,team_id=None):
        for record in self:
            if team_id:
                query = """UPDATE account_move_line 
                            SET team_id={id} WHERE move_id={move_id}""".format(id=team_id,move_id=record.move_id.id)
            
                self.env.cr.execute(query)
            elif record.move_id.team_id:
                query = """UPDATE account_move_line 
                            SET team_id=
                            (SELECT team_id from account_move WHERE id={id}) WHERE move_id={id}""".format(id=record.move_id.id)
                self.env.cr.execute(query)

   

class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner.balance.report.handler"

    team_id = fields.Many2one('crm.team')

    @api.model
    def _get_sql(self):
        super(ReportAccountAgedPartner, self)._get_sql()
        options = self.env.context['report_options']
        move_line_fields = self.env['account.move.line']._fields
        query = (""" 
            SELECT
                    {move_line_fields},
                    account_move_line.amount_currency as amount_currency,
        """).format(
            move_line_fields=self._get_move_line_fields('account_move_line')
        )
        if self.env['ir.model'].search([('model', '=', 'res.branch')]):
            query += ("""
                    account_move_line.branch_id AS branch_id,
            """)
        elif self.env['ir.module.module'].search([('name', '=', 'prosys_branch_management'), ('state', '=', 'installed')]):
            query += ("""
                    account_move_line.branch_id AS branch_id,
            """)
        if self.env['ir.module.module'].search([('name', '=', 'prosys_account_reports'), ('state', '=', 'installed')]):
            query += ("""
                    account_move_line.team_id AS team_id,
            """)
        
        query += ("""
                    
                    account_move_line.partner_id AS partner_id,
                    partner.name AS partner_name,
                    COALESCE(trust_property.value_text, 'normal') AS partner_trust,
                    COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
                    account_move_line.payment_id AS payment_id,
                    COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
                    account_move_line.expected_pay_date AS expected_pay_date,
                    move.move_type AS move_type,
                    move.name AS move_name,
                    move.invoice_date,
                    move.ref AS move_ref,
                    account.code || ' ' || account.name AS account_name,
                    account.code AS account_code,""" + ','.join([("""
                    CASE WHEN period_table.period_index = {i}
                    THEN %(sign)s * ROUND((
                        account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
                    ) * currency_table.rate, currency_table.precision)
                    ELSE 0 END AS period{i}""").format(i=i) for i in range(6)]) + """
                FROM account_move_line
                JOIN account_move move ON account_move_line.move_id = move.id
                JOIN account_journal journal ON journal.id = account_move_line.journal_id
                JOIN account_account account ON account.id = account_move_line.account_id
                LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
                LEFT JOIN ir_property trust_property ON (
                    trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
                    AND trust_property.name = 'trust'
                    AND trust_property.company_id = account_move_line.company_id
                )
                JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
                LEFT JOIN LATERAL (
                    SELECT part.amount, part.debit_move_id
                    FROM account_partial_reconcile part
                    WHERE part.max_date <= %(date)s
                ) part_debit ON part_debit.debit_move_id = account_move_line.id
                LEFT JOIN LATERAL (
                    SELECT part.amount, part.credit_move_id
                    FROM account_partial_reconcile part
                    WHERE part.max_date <= %(date)s
                ) part_credit ON part_credit.credit_move_id = account_move_line.id
                JOIN {period_table} ON (
                    period_table.date_start IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table.date_start)
                )
                AND (
                    period_table.date_stop IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table.date_stop)
                )
                WHERE account.internal_type = %(account_type)s
                AND account.exclude_from_aged_reports IS NOT TRUE
                GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
                         period_table.period_index, currency_table.rate, currency_table.precision
                HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
            """).format(
            currency_table=self.env['res.currency']._get_query_currency_table(options),
            period_table=self._get_query_period_table(options),
        )
        params = {
            'account_type': options['filter_account_type'],
            'sign': 1 if options['filter_account_type'] == 'receivable' else -1,
            'date': options['date']['date_to'],
        }
        return self.env.cr.mogrify(query, params).decode(self.env.cr.connection.encoding)

class ReportAccountAgedReceivable(models.AbstractModel):
    _inherit = "account.aged.receivable.report.handler"

    filter_salesteam = True

    @api.model
    def _get_options_domain(self, options, date_scope):
        domain = super(ReportAccountAgedReceivable, self)._get_options_domain(options, date_scope)
        if options.get('salesteam') and options.get('salesteams'):
            salesteams = [int(salesteam) for salesteam in options['salesteams']]
            domain.append(('team_id', 'in', salesteams))
        return domain

class ReportAccountAgedPayable(models.AbstractModel):
    _inherit = "account.aged.payable.report.handler"

    filter_salesteam = True

    @api.model
    def _get_options_domain(self, options, date_scope):
        domain = super(ReportAccountAgedPayable, self)._get_options_domain(options, date_scope)
        if options.get('salesteam') and options.get('salesteams'):
            salesteams = [int(salesteam) for salesteam in options['salesteams']]
            domain.append(('team_id', 'in', salesteams))
        return domain
