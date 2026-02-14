from odoo import models, fields, api


class SeriaflowPnlWizard(models.TransientModel):
    _name = 'seriaflow.pnl.wizard'
    _description = 'Profit & Loss Report Wizard'

    date_from = fields.Date(
        string='Dari Tanggal',
        required=True,
        default=lambda self: fields.Date.today().replace(month=1, day=1),
    )
    date_to = fields.Date(
        string='Sampai Tanggal',
        required=True,
        default=fields.Date.today,
    )

    def action_generate_report(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from.strftime('%Y-%m-%d'),
            'date_to': self.date_to.strftime('%Y-%m-%d'),
        }
        return self.env.ref(
            'seriaflow_accounting.action_report_pnl'
        ).report_action(self, data=data)

    @api.model
    def _get_report_data(self, date_from, date_to):
        """Get P&L report data."""
        # Income accounts
        income_accounts = self.env['seriaflow.account'].search([
            ('account_type', '=', 'income'),
        ])
        # Expense accounts
        expense_accounts = self.env['seriaflow.account'].search([
            ('account_type', '=', 'expense'),
        ])

        income_data = []
        total_income = 0.0
        for account in income_accounts:
            lines = self.env['seriaflow.journal.entry.line'].search([
                ('account_id', '=', account.id),
                ('entry_id.state', '=', 'posted'),
                ('entry_id.date', '>=', date_from),
                ('entry_id.date', '<=', date_to),
            ])
            credit = sum(lines.mapped('credit'))
            debit = sum(lines.mapped('debit'))
            balance = credit - debit
            if balance != 0:
                income_data.append({
                    'code': account.code,
                    'name': account.name,
                    'balance': balance,
                })
                total_income += balance

        expense_data = []
        total_expense = 0.0
        for account in expense_accounts:
            lines = self.env['seriaflow.journal.entry.line'].search([
                ('account_id', '=', account.id),
                ('entry_id.state', '=', 'posted'),
                ('entry_id.date', '>=', date_from),
                ('entry_id.date', '<=', date_to),
            ])
            debit = sum(lines.mapped('debit'))
            credit = sum(lines.mapped('credit'))
            balance = debit - credit
            if balance != 0:
                expense_data.append({
                    'code': account.code,
                    'name': account.name,
                    'balance': balance,
                })
                total_expense += balance

        return {
            'date_from': date_from,
            'date_to': date_to,
            'income_data': income_data,
            'total_income': total_income,
            'expense_data': expense_data,
            'total_expense': total_expense,
            'net_profit': total_income - total_expense,
        }
