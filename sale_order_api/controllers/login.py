# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

import logging, functools
import werkzeug.wrappers

from odoo.addons.sale_order_api.models.common import invalid_response, valid_response
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = request.env["api.access_token"].sudo().search([("token", "=", access_token)],
                                                                          order="id DESC", limit=1)

        if access_token_data.find_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.update_env(access_token_data.user_id.id)
        return func(self, *args, **kwargs)

    return wrap



class OdooController(http.Controller):

    @http.route("/api/login", methods=["GET"], type="http", auth="none", csrf=False)
    def api_login(self, **post):
        headers = request.httprequest.headers
        db = headers.get("db")
        username = headers.get("login")
        password = headers.get("password")
        _credentials_includes_in_headers = all([db, username, password])
        if not _credentials_includes_in_headers:
            return invalid_response(
                "missing error", "falta alguno de los siguientes datos [db, login,password]", 403,
            )
        try:
            request.session.authenticate(db, username, password)

        except AccessError as aee:
            return invalid_response("Access error", "Error: %s" % aee.name)
        except AccessDenied as ade:
            return invalid_response("Access denied", "Login, password or db invalid")
        except Exception as e:
            # Invalid database:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return invalid_response("wrong database name", error, 403)

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        # Generate tokens
        access_token = request.env["api.access_token"].find_or_create_token(user_id=uid, create=True)
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "uid": uid,
                    "partner_id": request.env.user.partner_id.id,
                    "access_token": access_token,
                    "company_name": request.env.user.company_name,
                    "country": request.env.user.country_id.name,
                    "contact_address": request.env.user.contact_address,
                }
            ),
        )


    @validate_token
    @http.route('/GET/invoices', type="http",methods=["GET"], auth="none", csrf=False)
    def read_invoices(self, **post):
        user_id = request.uid
        user_obj = request.env['res.users'].browse(user_id)
        sale_ids = request.env['sale.order'].with_user(user_obj).search([])
        values_list = []
        for sale in sale_ids:
            value_dict = {}
            value_dict["id"] = sale.id
            value_dict["createtime"] = sale.create_date.strftime("%Y-%m-%d %H:%M:%S")
            value_dict["document_number"] = "001-001-00001234"
            value_dict["customer"] = {}
            if sale.partner_id:
                if sale.partner_id.document_type=="CEDULA":
                    document_type="Cédula"
                elif sale.partner_id.document_type=="RUC":
                    document_type="RUC"
                else:
                    document_type="Pasaporte"
                value_dict["customer"]["document_type"] = sale.partner_id.document_type
                value_dict["customer"]["document_number"] = sale.partner_id.vat or "N/A"
                value_dict["customer"]["first_name"] = sale.partner_id.first_name or "N/A"
                value_dict["customer"]["last_name"] = sale.partner_id.last_name or "N/A"
                value_dict["customer"]["phone"] = sale.partner_id.mobile or "N/A"
                value_dict["customer"]["address"] = sale.partner_id.street or "N/A"
                value_dict["customer"]["email"] = sale.partner_id.email or "N/A"
            value_dict["items"] = []
            amount_tax = 0.00
            for line in sale.order_line:
                taxs = 0.00

                amount_discount = 0.00
                price = line.price_unit
                for tx in line.product_id.product_tmpl_id.taxes_id:
                    taxs += round(tx.amount, 2)
                    amount_tax = round(((taxs / 100) * price) * line.product_uom_qty, 2)
                if line.discount:
                    amount_discount = round(((line.discount / 100) * price) * line.product_uom_qty, 2)

                value_line = {"reference": line.product_id.name,
                              "price": round(price, 2),
                              "quantity": line.product_uom_qty,
                              "discount": amount_discount,
                              "subtotal": round(line.price_subtotal, 2),
                              "tax": round(amount_tax, 2),
                              "total": round(line.price_subtotal, 2) + round(amount_tax, 2),
                              }
                value_dict["items"].append(value_line)
            values_list.append(value_dict)

        
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                values_list
            ),
        )

    @validate_token
    @http.route('/POST/invoice', type="http", methods=["POST"],auth="none", csrf=False)
    def create_invoices(self, **post):
        user_id = request.uid
        user_obj = request.env['res.users'].browse(user_id)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        print(payload,"payloadpayloadpayloadpayload")
        partner_id = False
        if payload.get("customer"):
            if payload["customer"].get("document_number"):
                partner_id = request.env['res.partner'].search([("vat","=",payload["customer"].get("document_number"))],limit=1)
            else:
                info = "Customer Identification required"
                error = "Customer Identification required"
                _logger.error(info)
                return invalid_response(401, error, info)
            document_type=""
            if payload["customer"].get("document_type"):
                if payload["customer"].get("document_type")=="Cédula":
                    document_type="CEDULA"
                elif payload["customer"].get("document_type")=="RUC":
                    document_type="RUC"
                else:
                    document_type=="Pasaporte"
            first_name=""
            last_name=""
            if payload["customer"].get("first_name"):
                first_name=payload["customer"].get("first_name")
            if payload["customer"].get("last_name"):
                last_name=payload["customer"].get("last_name")

            dct_partner = {"name":payload["customer"].get("firs_name") or "",
                                                                        "vat":payload["customer"].get("document_number"),
                                                                        "document_type": document_type,
                                                                        "first_name":first_name,
                                                                        "last_name":last_name,
                                                                        "mobile":payload["customer"].get("phone") or "",
                                                                        "street":payload["customer"].get("address") or "",
                                                                        "email":payload["customer"].get("email") or "",}
            if not partner_id:
                partner_id = request.env['res.partner'].with_user(user_obj).create(dct_partner)
            else:
                partner_id.with_user(user_obj).write(dct_partner)

        else:
            info = "Customer required"
            error = "Customer required"
            _logger.error(info)
            return invalid_response(401, error, info)
        list_orderline=[]
        if payload.get("items"):
            for item in payload.get("items"):
                product_id=request.env['product.product'].search([("name","=",item.get("reference"))],limit=1)
                if not product_id:
                    product_id = request.env['product.product'].with_user(user_obj).create({"name":item.get("reference"),
                                                                        "lst_price":item.get("price")})

                discount=0
                tax=0
                if item.get("discount"):
                    discount = round(((item.get("discount")/item.get("quantity"))/price)*100,0)
                    tax = round(((item.get("discount")/item.get("quantity"))/price)*100,0)
                
                taxes_id=False
                if tax!=0:
                    taxes_id=request.env['account.tax'].search([("amount","=",tax),
                                                            ("type_tax_use","type_tax_use")],limit=1)
                list_orderline.append((0, 0, {
                                    'product_id': product_id.id,
                                    "price_unit": item.get("price"),
                                    "product_uom_qty": item.get("quantity"),
                                    "discount": discount,
                                    "tax_id":taxes_id.ids if taxes_id else False,                    
                                }))
        dct_sale = {
                    "partner_id":partner_id.id if partner_id else False,
                    "name":payload.get("document_number"),
                    "order_line":list_orderline,
                    "state":"draft"
                    }
        new_sale = request.env['sale.order'].with_user(user_obj).create(dct_sale)
        if new_sale:
            return valid_response([{"sale_id": new_sale.id, "message": "Sales created successfully"}], status=201)


    @validate_token
    @http.route(["/DELETE/invoice"], methods=["DELETE"], type="http", auth="none", csrf=False)
    def unlink_invoices(self, **post):
        user_id = request.uid
        user_obj = request.env['res.users'].browse(user_id)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        sale_id = payload.get("sale_id")
        sale_ids = request.env['sale.order'].with_user(user_obj).search([('id', '=', int(sale_id))])
        if sale_ids:
            sale_ids.unlink()
            return valid_response(
                [{"message": "Sales Id %s successfully deleted" % (sale_id,), "delete": True}])

        else:
            info = "Sale Id not Found"
            error = "Sale Id not Found"
            _logger.error(info)
            return invalid_response(401, error, info)
