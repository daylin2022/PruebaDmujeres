/** @odoo-module **/

import { PosGlobalState, PosSaleProductConfiguratorOrder} from 'point_of_sale.models';
import Registries from 'point_of_sale.Registries';

const NewPosGlobalState = (PosGlobalState) => class NewPosGlobalState extends PosGlobalState {
   async _processData(loadedData) {
    await super._processData(...arguments);
    this.packaging_ids = loadedData['product.packaging'] || [];
  
 }
}
const CustomOrderline = (PosSaleProductConfiguratorOrder) => class CustomOrderline extends PosSaleProductConfiguratorOrder{

   constructor(obj, options) {
      super(...arguments);
      var self = this;
      this.paquete = null;
      this.set_paquete();
   }
   set_paquete(set_paquete){
   // By default get the first channel
        this.paquete = set_paquete || this.pos.get_order().selected_orderline.packaging_ids[0] || null;
   }

   export_as_JSON(){
      const json = super.export_as_JSON(...arguments);
      json.packaging_id = this.packaging_id || null;
      return json;
   }

   init_from_JSON(json){
      super.init_from_JSON(...arguments);
      this.packaging_id = json.packaging_id;
   }

}
Registries.Model.extend(PosGlobalState, NewPosGlobalState);
Registries.Model.extend(PosSaleProductConfiguratorOrder, CustomOrderline);