from odoo import api,fields, models, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    arabic_name = fields.Char('Arabic Name')
    arabic_street = fields.Char('Arabic Street')
    arabic_street2 = fields.Char('Arabic Street2')
    arabic_city = fields.Char('Arabic City')
    arabic_state = fields.Char('Arabic State')
    arabic_country = fields.Char('Arabic Country')
    arabic_zip = fields.Char('Arabic Zip')
    arabic_web = fields.Char('Arabic Website')
    arabic_company_dis = fields.Char('Arabic  Company description')
    date_creation = fields.Datetime('Created Date', invisible=True, default=fields.Datetime.now)



class AccountPayment(models.Model):
    _inherit = 'account.payment'

    team_id = fields.Many2one(comodel_name='crm.team', string="Sales Team")

class AccountMove(models.Model):
    _inherit = 'account.move'

    team_id = fields.Many2one(comodel_name='crm.team', string="Sales Team")

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



