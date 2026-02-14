from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SeriaflowJournalEntry(models.Model):
    _name = 'seriaflow.journal.entry'
    _description = 'Journal Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Nomor',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    date = fields.Date(
        string='Tanggal',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    reference = fields.Char(
        string='Referensi',
        help='Nomor invoice, kwitansi, dll.',
    )
    narration = fields.Text(string='Keterangan')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancelled', 'Dibatalkan'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )
    line_ids = fields.One2many(
        'seriaflow.journal.entry.line',
        'entry_id',
        string='Detail Jurnal',
        copy=True,
    )
    total_debit = fields.Float(
        string='Total Debit',
        compute='_compute_totals',
        store=True,
    )
    total_credit = fields.Float(
        string='Total Credit',
        compute='_compute_totals',
        store=True,
    )
    is_balanced = fields.Boolean(
        string='Balanced',
        compute='_compute_totals',
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Perusahaan',
        default=lambda self: self.env.company,
    )
    line_count = fields.Integer(
        string='Jumlah Baris',
        compute='_compute_totals',
        store=True,
    )

    @api.depends('line_ids.debit', 'line_ids.credit')
    def _compute_totals(self):
        for entry in self:
            total_debit = sum(entry.line_ids.mapped('debit'))
            total_credit = sum(entry.line_ids.mapped('credit'))
            entry.total_debit = total_debit
            entry.total_credit = total_credit
            entry.is_balanced = abs(total_debit - total_credit) < 0.01
            entry.line_count = len(entry.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'seriaflow.journal.entry') or 'New'
        return super().create(vals_list)

    def action_post(self):
        for entry in self:
            if not entry.line_ids:
                raise ValidationError('Journal entry harus memiliki minimal 1 baris!')
            if not entry.is_balanced:
                raise ValidationError(
                    f'Journal entry {entry.name} tidak balance!\n'
                    f'Total Debit: {entry.total_debit:,.2f}\n'
                    f'Total Credit: {entry.total_credit:,.2f}'
                )
        self.write({'state': 'posted'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class SeriaflowJournalEntryLine(models.Model):
    _name = 'seriaflow.journal.entry.line'
    _description = 'Journal Entry Line'

    entry_id = fields.Many2one(
        'seriaflow.journal.entry',
        string='Journal Entry',
        required=True,
        ondelete='cascade',
        index=True,
    )
    account_id = fields.Many2one(
        'seriaflow.account',
        string='Akun',
        required=True,
    )
    description = fields.Char(string='Keterangan')
    debit = fields.Float(string='Debit', default=0.0)
    credit = fields.Float(string='Credit', default=0.0)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    date = fields.Date(
        related='entry_id.date',
        store=True,
        string='Tanggal',
    )

    @api.constrains('debit', 'credit')
    def _check_debit_credit(self):
        for line in self:
            if line.debit < 0 or line.credit < 0:
                raise ValidationError('Debit dan Credit tidak boleh negatif!')
            if line.debit > 0 and line.credit > 0:
                raise ValidationError('Satu baris hanya boleh diisi Debit ATAU Credit, tidak keduanya!')
