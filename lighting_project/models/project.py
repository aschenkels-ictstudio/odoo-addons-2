# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time


def get_years():
    year_list = []
    for i in range(1990, 2100):
        year_list.append((i, str(i)))
    return year_list


class LightingProject(models.Model):
    _name = 'lighting.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _description = 'Project'

    name = fields.Char(string='Name', required=True, track_visibility='onchange')

    city = fields.Char(string='City', required=True, track_visibility='onchange')
    country_id = fields.Many2one(comodel_name='res.country', ondelete='restrict', string='Country', required=True)
    type_ids = fields.Many2many(comodel_name='lighting.project.type', string='Types',
                                relation='lighting_project_product_type_rel',
                                column1='project_id', column2='type_id', required=True, track_visibility='onchange')

    prescriptor = fields.Char(string='Prescriptor', track_visibility='onchange')

    year = fields.Selection(selection=get_years(), string='Year',
                            default=int(time.strftime('%Y')), track_visibility='onchange')
    family_ids = fields.Many2many(comodel_name='lighting.product.family', string='Families',
                                  relation='lighting_project_product_family_rel',
                                  column1='project_id', column2='family_id', required=True, track_visibility='onchange')

    description = fields.Text(string="Description", translate=True, track_visibility='onchange')

    agent_id = fields.Many2one(comodel_name='lighting.project.agent', required=True, track_visibility='onchange')

    auth_contact_name = fields.Char(string="Name", track_visibility='onchange')
    auth_contact_email = fields.Char(string="e-mail", track_visibility='onchange')
    auth_contact_phone = fields.Char(string="Phone", track_visibility='onchange')

    attachment_ids = fields.One2many(comodel_name='lighting.project.attachment',
                                     inverse_name='project_id', string='Attachments', copy=True, track_visibility='onchange')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.project.attachment'] \
                .search_count([('project_id', '=', record.id)])

    catalog_ids = fields.Many2many(compute='_compute_catalog_ids', comodel_name='lighting.catalog',
                                   string='Catalogs', readonly=True, track_visibility='onchange')

    @api.depends('family_ids')
    def _compute_catalog_ids(self):
        for record in self:
            record.catalog_ids = self.env['lighting.product'] \
                .search([('family_ids', 'in', record.family_ids.mapped('id'))]) \
                .mapped('catalog_ids')

    @api.multi
    def print_project_sheet(self):
        return self.env.ref('lighting_project.project_sheet_report_action').report_action(self)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The keyword must be unique!'),
                        ]
