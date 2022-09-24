from http.client import BAD_REQUEST, HTTPResponse
import structlog
from django.http import HttpResponse
import json
import dateutil.parser
from xero import Xero
from xero_api.models import XeroEfrisClientCredentials
from xero.auth import OAuth2Credentials
from mita_api.services import send_mita_request

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
        currency = good_instance['currency']
        measure_unit = good_instance['measure_unit']
        commodity_tax_category = good_instance['commodity_tax_category']
        xero_tax_rate = good_instance['xero_tax_rate']
        description = good_instance['description']
        account_code = good_instance['xero_purchase_account']
        client_account_id = good_instance['client_account_id']
        is_product = True
        is_purchased = True

        new_product = {

            "Code": goods_code,

            "PurchaseDetails": {
                "UnitPrice": purchase_price,
                "AccountCode": account_code,
                "TaxType": xero_tax_rate
            },
            "SalesDetails": {
                "UnitPrice": unit_price,
                "AccountCode": account_code,
                "TaxType": xero_tax_rate
            },
            "Name": goods_name,
            "IsTrackedAsInventory": is_product,
            "IsSold": True,
            "IsPurchased": is_purchased
        }

        client_data = get_xero_client_data(client_account_id)

        cred_state = client_data.cred_state
        credentials = OAuth2Credentials(**cred_state)

        struct_logger.info(event='create_xero_goods_configuration', client_data=client_data.cred_state,
                           account=good_instance, credentials=type(credentials))

        if credentials.expired():
            credentials.refresh()
            client_data.cred_state = credentials.state
            client_data.save()

        xero = Xero(credentials)
        item = xero.items.put(new_product)

        struct_logger.info(event='create_xero_goods_configuration',
                           xero_product=item, account=good_instance)

        efris_stock_configuration_payload = {
            "goods_name": goods_name,
            "goods_code": goods_code,
            "unit_price": unit_price,
            "measure_unit": measure_unit,
            "currency": currency,
            "commodity_tax_category": commodity_tax_category,
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

        struct_logger.info(event=create_xero_goods_adjustment,
                           product=good_instance,
                           )

        xero_invoice_type = good_instance['xero_invoice_type']
        goods_code = good_instance['goods_code']
        purchase_price = good_instance['purchase_price']
        supplier = good_instance['supplier']
        supplier_tin = good_instance['supplier_tin']
        quantity = good_instance['quantity']
        stock_in_type = good_instance['stock_in_type']
        adjust_type = good_instance['adjust_type']
        operation_type = good_instance['operation_type']
        purchase_remarks = good_instance['purchase_remarks']
        xero_tax_rate = good_instance['xero_tax_rate']
        account_code = good_instance['xero_purchase_account']
        currency = good_instance['currency']
        client_account_id = good_instance['client_account_id']

        line_items = []

        if adjust_type is None:
            adjust_type = ""

        client_data = get_xero_client_data(client_account_id)

        cred_state = client_data.cred_state
        credentials = OAuth2Credentials(**cred_state)
        if credentials.expired():
            credentials.refresh()
            client_data.cred_state = credentials.state
            client_data.save()
        xero = Xero(credentials)

        contact = xero.contacts.get(u'39efa556-8dda-4c81-83d3-a631e59eb6d3')

        line_item = {
            "ItemCode": goods_code,
            "Description": purchase_remarks,
            "Quantity": quantity,
            "UnitAmount": purchase_price,
            "TaxType": xero_tax_rate,
            "AccountCode": "300"
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

        struct_logger.info(event=create_xero_goods_adjustment,
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
        struct_logger.error(event=create_xero_goods_adjustment,
                            error=str(ex),

                            )

def get_xero_client_data(client_account_id):
    try:

        client_data = XeroEfrisClientCredentials.objects.get(id=client_account_id)
        struct_logger.info(event='get_client_data', client_id=client_account_id, data=client_data,
                           msg='Retrieving account client data')
        return client_data

    except Exception as ex:

        struct_logger.info(event='get_client_data', error=str(ex), client=client_account_id)

        raise BAD_REQUEST('Invalid request: Can not find client account {}'.format(str(ex)))


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
                           dt=type(data),
                           invoice_id=invoice_id,
                           event_type=event_type,
                           event_category=event_category
                           )

        cred_state = client_data.cred_state
        credentials = OAuth2Credentials(**cred_state)
        if credentials.expired():
            credentials.refresh()
            client_data.cred_state = credentials.state
            client_data.save()
        xero = Xero(credentials)

        invoices = xero.invoices.get(u'{}'.format(invoice_id))

        generate_mita_invoice(invoices, client_data)

        return HttpResponse("invoices retrieved {}".format(invoices))

    except Exception as ex:
        return HttpResponse("invoices not retrieved {}".format(str(ex)))


def generate_mita_invoice(xero_invoices, client_data):
    for xero_invoice in xero_invoices:

        if xero_invoice['Status'] == "AUTHORISED":

            try:

                xero_credit_note = xero_invoice['CreditNotes'][0]
                cred_state = client_data.cred_state
                credentials = OAuth2Credentials(**cred_state)
                if credentials.expired():
                    credentials.refresh()
                    client_data.cred_state = credentials.state
                    client_data.save()
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

                if contact_groups[0]["Name"] in ("Business", "Government"):
                    buyer_type = "0"

                elif contact_groups[0]["Name"] == "Foreignor":
                    buyer_type = "2"

                else:

                    buyer_type = "1"

                try:
                    buyer_tax_pin = xero_invoice['Contact']['CompanyNumber']

                except Exception as ex:

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
                        "invoice_code": xero_invoice['InvoiceID'],
                        "cashier": "Eseza Muwanga",
                        "payment_mode": "107",
                        "currency": xero_invoice['CurrencyCode'],
                        "invoice_type": "1",
                        "invoice_kind": "1",
                        "goods_description": xero_invoice['InvoiceNumber'],
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
            send_mita_request('invoice/issue', mita_payload, client_data)
