from odoo import models, fields, api
from odoo.osv.expression import AND, OR

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('product.packaging')
        return result

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('packaging_ids')
        return result

    def _loader_params_product_packaging(self):
        return {
            'search_params': {
                'domain': [('sales', '=', True)],
                'fields': ['name', 'barcode', 'product_id', 'qty','product_uom_id'],
            },
        }

    def _get_pos_ui_product_packaging(self,  params):
        print('params', params)
        return self.env['product.packaging'].search_read(**params['search_params'])