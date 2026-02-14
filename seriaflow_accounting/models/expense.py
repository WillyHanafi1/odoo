from odoo import models, fields, api


class SeriaflowExpense(models.Model):
    _name = 'seriaflow.expense'
    _description = 'Expense Tracker'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Deskripsi',
        required=True,
    )
    date = fields.Date(
        string='Tanggal',
        required=True,
        default=fields.Date.context_today,
    )
    amount = fields.Float(
        string='Jumlah (Rp)',
        required=True,
    )
    category = fields.Selection(
        selection=[
            ('operational', 'Operasional'),
            ('marketing', 'Marketing'),
            ('salary', 'Gaji & Upah'),
            ('tools', 'Tools & Software'),
            ('travel', 'Perjalanan'),
            ('office', 'Perlengkapan Kantor'),
            ('other', 'Lainnya'),
        ],
        string='Kategori',
        required=True,
        default='operational',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Diajukan'),
            ('approved', 'Disetujui'),
            ('rejected', 'Ditolak'),
        ],
        string='Status',
        default='draft',
    )
    account_id = fields.Many2one(
        'seriaflow.account',
        string='Akun Beban',
        domain=[('account_type', '=', 'expense')],
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor/Supplier',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Diajukan Oleh',
        default=lambda self: self.env.user,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Disetujui Oleh',
        readonly=True,
    )
    attachment = fields.Binary(
        string='Bukti/Nota',
        attachment=True,
    )
    attachment_name = fields.Char(string='Nama File')
    note = fields.Text(string='Catatan')
    journal_entry_id = fields.Many2one(
        'seriaflow.journal.entry',
        string='Journal Entry',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Perusahaan',
        default=lambda self: self.env.company,
    )

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        for expense in self:
            expense.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
            })
            # Auto-create journal entry if account is set
            if expense.account_id:
                expense._create_journal_entry()

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_draft(self):
        self.write({'state': 'draft', 'approved_by': False})

    def _create_journal_entry(self):
        self.ensure_one()
        # Find cash/bank account
        cash_account = self.env['seriaflow.account'].search([
            ('code', '=', '1-1001'),
            ('company_id', '=', self.company_id.id),
        ], limit=1)

        if not cash_account:
            return

        entry = self.env['seriaflow.journal.entry'].create({
            'date': self.date,
            'reference': f'Expense: {self.name}',
            'narration': self.note or f'Pengeluaran: {self.name}',
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_id.id,
                    'description': self.name,
                    'debit': self.amount,
                    'credit': 0.0,
                    'partner_id': self.partner_id.id if self.partner_id else False,
                }),
                (0, 0, {
                    'account_id': cash_account.id,
                    'description': self.name,
                    'debit': 0.0,
                    'credit': self.amount,
                    'partner_id': self.partner_id.id if self.partner_id else False,
                }),
            ],
        })
        entry.action_post()
        self.journal_entry_id = entry.id
