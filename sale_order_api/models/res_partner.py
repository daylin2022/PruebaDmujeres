# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    document_type=fields.Selection([('CEDULA', 'CEDULA'), ('RUC', 'RUC'), ('PASAPORTE', 'PASAPORTE')], u"Tipo de Identificación"
                             , track_visibility='onchange', copy=False, default='CEDULA')

    first_name = fields.Char('Primer Nombre', size=20, track_visibility='onchange')
    second_name = fields.Char('Segundo Nombre', size=20, track_visibility='onchange')
    last_name = fields.Char('Apellido', size=60, track_visibility='onchange')


    @api.onchange("first_name","second_name","last_name")
    @api.constrains("first_name","second_name","last_name")
    def get_name_partner(self):
        for l in self:
            name=""
            if l.first_name:
                name+=l.first_name+" "
            if l.second_name:
                name+=l.second_name+" "
            if l.last_name:
                name+=l.last_name
            l.name = name

