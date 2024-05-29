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




class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    team_id = fields.Many2one('crm.team')




