// This is how you define a new JavaScript module in Odoo
odoo.define('p021_pos.PaquetesButton', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('@web/core/utils/hooks');

    class PaquetesButton extends PosComponent {
        setup(){
            super.setup();
            useListener('click', this.onCLick);
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }
         get currentPaqueteName() {
            const order = this.currentOrder;
            let line_select = order.selected_orderline
            if (line_select && line_select.product){
            return line_select.product.packaging_ids
                ? line_select.product.packaging_ids.name
                : this.env._t('Channel');
            }
         }

        async onCLick() {
            let order = this.env.pos.get_order()
            let line_select = order.selected_orderline
            if (line_select && line_select.product){
            const paquetes = Object.values(line_select.product.packaging_ids);
            if (paquetes.length!=0){
            const selectionList  = this.env.pos.packaging_ids.map(packing => ({
                                id: packing.id,
                                label: packing.name +" por: " + packing.qty.toFixed(2) + " " +packing.product_uom_id[1],
                                qty: packing.qty,
                                item: packing,
                            }));

                const filteredSelectionList = selectionList.filter(packing => paquetes.includes(packing.id));
                if (filteredSelectionList.length != 0){
                    const { confirmed, payload: selectedPaquete } = await this.showPopup(
                    'SelectionPopup',
                    {
                        title: this.env._t('Seleccione un empaquetado.'),
                        list: filteredSelectionList,
                    }
                    );
                    if (confirmed) {
                        const order = this.currentOrder;
                        let line_select = order.selected_orderline
                        order.selected_orderline.set_quantity(selectedPaquete.qty)
                        }
                }

                else {
                    await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Not Found'),
                        body: _.str.sprintf(
                            this.env._t('Este producto no cuenta con empaquetados configurados'),
                        ),
                        confirmText: this.env._t('OK'),
                    });
                }
            }
            else{
            await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Not Found'),
                        body: _.str.sprintf(
                           this.env._t('Este producto no cuenta con empaquetados configurados'),
                        ),
                        confirmText: this.env._t('OK'),
                    });
                }
           }
        }
       }

    PaquetesButton.template = 'PaquetesButton';
    ProductScreen.addControlButton({
        component: PaquetesButton,
        position: ['before', 'OrderlineCustomerNoteButton'] // [Position, RelativeToComponent]
    });

    Registries.Component.add(PaquetesButton);
    return PaquetesButton;

});