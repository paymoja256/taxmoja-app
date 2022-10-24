from http.client import BAD_REQUEST, HTTPResponse
import structlog
from django.http import HttpResponse
import json
import dateutil.parser
from xero import Xero
from efris.models import EfrisCommodityCategories, EfrisCurrencyCodes, EfrisMeasureUnits
from xero_api.models import XeroEfrisClientCredentials, XeroEfrisGoodsConfiguration
from xero.auth import OAuth2Credentials
from mita_api.services import send_mita_request
from django.shortcuts import get_object_or_404

struct_logger = structlog.get_logger(__name__)


def create_xero_goods_configuration(good_instance):
    try:
        struct_logger.info(event='create_xero_goods_configuration',
                           product=good_instance,
                           )
        goods_name = good_instance['goods_name']
        goods_code = good_instance['goods_code']
        purchase_price = good_instance['unit_price']
        unit_price = good_instance['unit_price']
        description = good_instance['description']

        currency = get_object_or_404(
            EfrisCurrencyCodes, pk=good_instance['currency_id'])
        measure_unit = get_object_or_404(
            EfrisMeasureUnits, pk=good_instance['measure_unit_id'])
        efris_commodity_tax_category = get_object_or_404(
            EfrisCommodityCategories, pk=good_instance['commodity_tax_category_id'])
        client_data = get_object_or_404(
            XeroEfrisClientCredentials, pk=good_instance['client_account_id'])

        xero_tax_rate = client_data.xero_standard_tax_rate_code
        if efris_commodity_tax_category.tax_rate == 0.00:
            xero_tax_rate = client_data.xero_exempt_tax_rate_code
        xero_purchase_account_code = client_data.xero_purchase_account
        is_product = True
        is_purchased = True

        

        new_product = {

            "Code": goods_code,

            "PurchaseDetails": {
                "UnitPrice": purchase_price,
                "AccountCode": xero_purchase_account_code,
                "TaxType": xero_tax_rate
            },
            "SalesDetails": {
                "UnitPrice": unit_price,
                "AccountCode": xero_purchase_account_code,
                "TaxType": xero_tax_rate
            },
            "Name": goods_name,
            "IsTrackedAsInventory": is_product,
            "IsSold": True,
            "IsPurchased": is_purchased
        }

      

        struct_logger.info(event='create_xero_goods_configuration', client_data=client_data.cred_state,
                           account=good_instance)

        credentials = xero_client_credentials(client_data)
        xero = Xero(credentials)
        item = xero.items.put(new_product)

        struct_logger.info(event='create_xero_goods_configuration',
                           xero_product=item, account=good_instance)

        efris_stock_configuration_payload = {
            "goods_name": goods_name,
            "goods_code": goods_code,
            "unit_price": unit_price,
            "measure_unit": measure_unit.measure_unit_code,
            "currency": currency.currency_code,
            "commodity_tax_category": efris_commodity_tax_category.efris_commodity_category_code,
            "goods_description": description
        }

        struct_logger.info(event='create_xero_goods_configuration',
                           efris_product=efris_stock_configuration_payload,
                           account=good_instance
                           )
        efris_response = send_mita_request(
            'stock/configuration', efris_stock_configuration_payload, client_data)
        return HttpResponse("xero Item saved {}  \n EFRIS Item Saved {} ".format(item, efris_response))
    except Exception as ex:
        struct_logger.error(event='create_xero_goods_configuration',
                            error=ex,

                            )
        return HttpResponse("Error in Goods Configuration {}   ".format(str(ex)))


def create_xero_goods_adjustment(good_instance):
    try:

        struct_logger.info(event='create_xero_goods_adjustment',
                           product=good_instance,
                           )

        xero_invoice_type = good_instance['xero_invoice_type']
        
        purchase_price = good_instance['purchase_price']
        supplier = good_instance['supplier']
        supplier_tin = good_instance['supplier_tin']
        quantity = good_instance['quantity']
        stock_in_type = good_instance['stock_in_type']
        adjust_type = good_instance['adjust_type']
        operation_type = good_instance['operation_type']
        purchase_remarks = good_instance['purchase_remarks']
        
        
        goods_details= get_object_or_404(
            XeroEfrisGoodsConfiguration,pk=good_instance['good_id'])
        
        
        client_data = goods_details.client_account
        # print(client_data.__dict__)
        # print(client_data.cred_state)
        cred_state = goods_details.client_account.cred_state
        credentials = xero_client_credentials(client_data)
        xero = Xero(credentials)
        print(credentials)
        print(client_data.xero_stock_in_contact_account)
        contact =xero.contacts.all()[0]
        xero_tax_rate = client_data.xero_standard_tax_rate_code
        if goods_details.commodity_tax_category.tax_rate == 0.00:
            xero_tax_rate = client_data.xero_exempt_tax_rate_code
        print('contact', contact)
        goods_code =goods_details.goods_code

        line_items = []

        if adjust_type is None:
            adjust_type = ""

        

        line_item = {
            "ItemCode": goods_code,
            "Description": purchase_remarks,
            "Quantity": quantity,
            "UnitAmount": purchase_price,
            "TaxType": xero_tax_rate,
            "AccountCode": client_data.xero_purchase_account
        }

        line_items.append(line_item)

        invoice = {
            "LineItems": line_items,
            "Contact": contact,
            "DueDate": dateutil.parser.parse("2020-09-03T00:00:00Z"),
            "Date": dateutil.parser.parse("2020-07-03T00:00:00Z"),
            "Type": xero_invoice_type,
            "Status": "AUTHORISED"
        }

        invoice = xero.invoices.put(invoice)

        struct_logger.info(event='create_xero_goods_adjustment',
                           xero_invoice=invoice,
                           )

        efris_stock_adjustment_payload = {
            "goods_code": goods_code,
            "supplier": supplier,
            "supplier_tin": supplier_tin,
            "stock_in_type": stock_in_type,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "purchase_remarks": purchase_remarks,
            "operation_type": operation_type,
            "adjust_type": adjust_type,
        }

        mita_stock = send_mita_request(
            'stock/adjustment', efris_stock_adjustment_payload, client_data)

        return HTTPResponse("xero Adjustment saved {}  \n Efris Item Saved {} ".format(invoice, mita_stock))

    except Exception as ex:
        struct_logger.error(event='create_xero_goods_adjustment',
                            error=str(ex),

                            )
        return HttpResponse("Error in Goods Adjustment {}   ".format(str(ex)))



def xero_send_invoice_data(request, client_data):
    try:
        data = json.loads(request.decode('utf8').replace("'", '"'))
        data = data['events'][0]
        invoice_id = data['resourceId']
        event_type = data['eventType']
        event_category = data['eventCategory']
        tenant_id = data['tenantId']

        struct_logger.info(event="xero_incoming_invoice",
                           xero_data=data,
                           dt=data,
                           invoice_id=invoice_id,
                           event_type=event_type,
                           event_category=event_category
                           )

        credentials = xero_client_credentials(client_data)
        xero = Xero(credentials)

        invoices = xero.invoices.get(u'{}'.format(invoice_id))
        
        print(invoices)

        generate_mita_invoice(invoices, client_data)

        return HttpResponse("invoices retrieved {}".format(invoices))

    except Exception as ex:
        return HttpResponse("invoices not retrieved {}".format(str(ex)))


def generate_mita_invoice(xero_invoices, client_data):
    for xero_invoice in xero_invoices:
        # if xero_invoice['Status'] in ("AUTHORISED"):
        if xero_invoice['Status'] in ("AUTHORISED", "PAID"):

            try:

                xero_credit_note = xero_invoice['CreditNotes'][0]
                credentials = xero_client_credentials(client_data)
                xero = Xero(credentials)
                credit_note = xero.creditnotes.get(
                    u'{}'.format(xero_credit_note['ID']))
                print('credit note:{}'.format(credit_note))

                xero_invoice = credit_note[0]

                print('xero invoice:{}'.format(xero_invoice))

                is_export = False
                is_priviledged = False
                goods_details = []
                buyer_type = "0"
                try:
                    contact_groups = xero_invoice['Contact']['ContactGroups']

                    if contact_groups[0]["Name"] in ("Business", "Government"):
                        buyer_type = "0"

                    elif contact_groups[0]["Name"] == "Foreignor":
                        buyer_type = "2"

                    else:

                        buyer_type = "1"
                except Exception as ex:

                    buyer_tax_pin = ""

                try:
                    buyer_tax_pin = xero_invoice['Contact']['CompanyNumber']

                except Exception as ex:

                    buyer_tax_pin = ""

                try:
                    original_invoice = xero_invoice['Allocations'][0]['Invoice']
                except Exception as ex:

                    print("original invoice not found")

                    original_invoice = xero_invoices[0]

                for good in xero_invoice['LineItems']:
                    mita_good = {
                        "good_code": good['ItemCode'],
                        "quantity": good['Quantity'],
                        "sale_price": good['UnitAmount'],
                        "tax_category": good['TaxType']
                    }
                    goods_details.append(mita_good)

                mita_payload = {
                    "invoice_details": {
                        "invoice_code": xero_invoice['CreditNoteID'],
                        "cashier": "Eseza Muwanga",
                        "payment_mode": "107",
                        "currency": xero_invoice['CurrencyCode'],
                        "invoice_type": "1",
                        "invoice_kind": "1",
                        "goods_description": xero_invoice['CreditNoteNumber'],
                        "industry_code": "",
                        "original_instance_invoice_id": original_invoice['InvoiceID'],
                        "return_reason": xero_invoice['Reference'],
                        "return_reason_code": "105",
                        "is_export": is_export
                    },
                    "goods_details": goods_details,
                    "buyer_details": {
                        "tax_pin": buyer_tax_pin,
                        "nin": "",
                        "passport_number": "",
                        "legal_name": xero_invoice['Contact']['Name'],
                        "business_name": "",
                        "address": "",
                        "email": "",
                        "mobile": "",
                        "buyer_type": buyer_type,
                        "buyer_citizenship": "",
                        "buyer_sector": "",
                        "buyer_reference": "",
                        "is_privileged": is_priviledged,
                        "local_purchase_order": ""
                    },
                    "instance_invoice_id": xero_invoice['ID']

                }
                print(mita_payload)

            except Exception as ex:

                is_export = False
                is_priviledged = False
                goods_details = []
                buyer_type = "0"

                contact_groups = xero_invoice['Contact']['ContactGroups']

                if contact_groups[0]["Name"] in ("Business","business","Government"):
                    buyer_type = "0"

                elif contact_groups[0]["Name"] == "Foreignor":
                    buyer_type = "2"

                else:

                    buyer_type = "1"

                try:
                    buyer_tax_pin = xero_invoice['Contact']['TaxNumber']

                except Exception as ex:
                    buyer_type = "1"
                    buyer_tax_pin = ""

                for good in xero_invoice['LineItems']:
                    mita_good = {
                        "good_code": good['ItemCode'],
                        "quantity": good['Quantity'],
                        "sale_price": good['UnitAmount'],
                        "tax_category": good['TaxType']
                    }
                    goods_details.append(mita_good)

                mita_payload = {
                    "invoice_details": {
                        "invoice_code":xero_invoice['InvoiceID'],
                        "cashier": "Eseza Muwanga",
                        "payment_mode": "107",
                        "currency": xero_invoice['CurrencyCode'],
                        "invoice_type": "1",
                        "invoice_kind": "1",
                        "goods_description":  xero_invoice['Reference'],
                        "industry_code": "",
                        "original_instance_invoice_id": "",
                        "return_reason": "",
                        "return_reason_code": "",
                        "is_export": is_export
                    },
                    "goods_details": goods_details,
                    "buyer_details": {
                        "tax_pin": buyer_tax_pin,
                        "nin": "",
                        "passport_number": "",
                        "legal_name": xero_invoice['Contact']['Name'],
                        "business_name": "",
                        "address": "",
                        "email": "",
                        "mobile": "",
                        "buyer_type": buyer_type,
                        "buyer_citizenship": "",
                        "buyer_sector": "",
                        "buyer_reference": "",
                        "is_privileged": is_priviledged,
                        "local_purchase_order": ""
                    },
                    "instance_invoice_id": xero_invoice['InvoiceID']

                }
                print(mita_payload)
            send_mita_request('invoice/queue', mita_payload, client_data)



def xero_client_credentials(client_data):
    cred_state = client_data.cred_state
    credentials = OAuth2Credentials(**cred_state)
    if credentials.expired():
        credentials.refresh()
        client_data.cred_state = credentials.state
        client_data.save()
    return credentials