from odoo import models, fields, api


class SeriaflowAccount(models.Model):
    _name = 'seriaflow.account'
    _description = 'Chart of Accounts'
    _order = 'code'
    _rec_name = 'display_name'

    code = fields.Char(
        string='Kode Akun',
        required=True,
        index=True,
    )
    name = fields.Char(
        string='Nama Akun',
        required=True,
    )
    display_name = fields.Char(
        string='Akun',
        compute='_compute_display_name',
        store=True,
    )
    account_type = fields.Selection(
        selection=[
            ('asset', 'Aset'),
            ('liability', 'Kewajiban'),
            ('equity', 'Modal'),
            ('income', 'Pendapatan'),
            ('expense', 'Beban'),
        ],
        string='Tipe Akun',
        required=True,
    )
    parent_id = fields.Many2one(
        'seriaflow.account',
        string='Akun Induk',
        ondelete='restrict',
    )
    child_ids = fields.One2many(
        'seriaflow.account',
        'parent_id',
        string='Sub Akun',
    )
    balance = fields.Float(
        string='Saldo',
        compute='_compute_balance',
        store=False,
    )
    note = fields.Text(string='Catatan')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Perusahaan',
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)',
         'Kode akun harus unik per perusahaan!'),
    ]

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rec in self:
            if rec.code and rec.name:
                rec.display_name = f"[{rec.code}] {rec.name}"
            else:
                rec.display_name = rec.name or ''

    def _compute_balance(self):
        for account in self:
            lines = self.env['seriaflow.journal.entry.line'].search([
                ('account_id', '=', account.id),
                ('entry_id.state', '=', 'posted'),
            ])
            total_debit = sum(lines.mapped('debit'))
            total_credit = sum(lines.mapped('credit'))
            if account.account_type in ('asset', 'expense'):
                account.balance = total_debit - total_credit
            else:
                account.balance = total_credit - total_debit
