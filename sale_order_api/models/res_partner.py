# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    document_type=fields.Selection([('CEDULA', 'CEDULA'), ('RUC', 'RUC'), ('PASAPORTE', 'PASAPORTE')], u"Tipo de Identificación"
                             , track_visibility='onchange', copy=False, default='CEDULA')
