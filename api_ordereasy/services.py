from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import structlog
import requests
from api_mita.services import send_mita_request
from .models import OEEfrisClientCredentials


struct_logger = structlog.get_logger(__name__)


def process_invoice(response, client_acc_id):
    try:
        # Get local client
        client_data = get_object_or_404(OEEfrisClientCredentials, pk=client_acc_id)
        # retrieving invoice data
        invoice_data = response

        goods_details = invoice_data["ProjectLines"]

        # retrieving customer data
        customer = invoice_data["ManualClient"]

        struct_logger.info(
            event="create_outgoing_oe_invoice",
            invoice_data=invoice_data,
            customer_data=customer,
        )

        # Get variables

        tax_pin = customer["VATNumber"]

        # is_export = clean_export(customer, client_data)

        cashier = invoice_data["SalesRep"]

        is_business = bool(customer["CompanyName"].strip())

        buyer_type = clean_buyer_type(is_business)

        industry_code = "101"

        is_export = False
        buyer_type = clean_buyer_type(customer, client_data)

        # Validate tax_pin

        if buyer_type in "0" and tax_pin == "":
            struct_logger.error(
                event="oe_invoice_processing",
                message="Buyer is a business, tax pin should not be empty",
            )

        buyer_details = clean_buyer_details(customer, buyer_type, tax_pin)

        goods_details = clean_goods_details(goods_details)

        tax_invoice = create_efris_invoice(
            invoice_data,
            industry_code,
            buyer_details,
            cashier,
            goods_details,
            client_data,
            is_export,
            payment_mode="102",
            invoice_type="1",
            invoice_kind="1",
        )

        struct_logger.info(
            event="oe_invoice_processing",
            message="Sending invoice to mita",
            response=tax_invoice,
        )

        return tax_invoice

    except Exception as ex:
        struct_logger.error(
            event="dear invoice processing",
            message="Failed to process invoice",
            error=ex,
        )
        return ex


def process_credit_note(response, client_acc_id):
    try:
        # Get local client
        client_data = get_object_or_404(DearEfrisClientCredentials, pk=client_acc_id)

        # retrieving credit_note data

        task_id = response["SaleID"]
        url = "/sale/creditnote?SaleID={}".format(task_id)

        invoice_data = send_oe_api_request(url)

        # invoices = invoice_data["Invoices"]
        credit_notes = invoice_data["CreditNotes"]

        # Old invoice data

        url = "/sale?ID={}".format(task_id)
        invoice_data = send_oe_api_request(url)

        goods_details = []

        # retrieving customer data

        url = "/customer?ID={}".format(invoice_data["CustomerID"])
        customer_data = send_oe_api_request(url)
        customer = customer_data["CustomerList"][0]

        struct_logger.info(
            event="create_outgoing_dear_credit_note",
            invoice_data=invoice_data,
            customer_data=customer,
        )

        # Get variables

        tax_pin = clean_tax_pin(customer, client_data)

        is_export = clean_export(customer, client_data)

        cashier = clean_cashier(response, customer, client_data)

        industry_code = "101"
        if is_export == True:
            industry_code = "102"
        buyer_type = clean_buyer_type(customer, client_data)

        # Validate tax_pin

        if buyer_type in "0" and tax_pin == "":
            struct_logger.error(
                event="create_outgoing_dear_credit_note",
                message="Buyer is a business, tax pin should not be empty",
            )

        buyer_details = clean_buyer_details(invoice_data, buyer_type, tax_pin)

        goods_details, invoice = clean_goods_details(credit_notes)

        tax_invoice = create_efris_invoice(
            invoice,
            invoice_data,
            industry_code,
            buyer_details,
            cashier,
            goods_details,
            client_data,
            is_export,
            payment_mode="102",
            invoice_type="1",
            invoice_kind="1",
            credit_notes=credit_notes,
        )

        struct_logger.info(
            event="create_outgoing_dear_credit_note",
            message="Sending invoice to mita",
            response=tax_invoice,
        )

        return tax_invoice

    except Exception as ex:
        struct_logger.error(
            event="dear_invoice_processing",
            message="Sending invoice to mita",
            response=str(ex),
        )
        return str(ex)


def send_oe_api_request(url: str, client_acc_id):
    try:
        client_data = get_object_or_404(OEEfrisClientCredentials, pk=client_acc_id)
        url = "{}/{}".format(client_data.oe_url, url)

        payload = {}
        headers = {"X-OrderEazi-Key": client_data.oe_api_key}

        struct_logger.info(
            event="send_oe_request",
            url=url,
            header=headers,
            msg="Sending ordereasy request",
        )

        response = requests.request("GET", url, headers=headers, data=payload)

        struct_logger.info(
            event="send_oe_request",
            url=url,
            header=headers,
            response=response.text,
            msg="Sending ordereasy request",
        )

        return response.json()

    except Exception as ex:
        return {"message": "Ordereasy API is unvailable {}".format(str(ex))}


def clean_currency_product(currency):
    if currency == "UGX" or currency == "101":
        return "101"
    elif currency == "USD" or currency == "102":
        return "102"
    elif currency == "EUR" or currency == "104":
        return "104"


def get_tax_rate(tax_rule):
    if tax_rule.upper() == "VAT":
        return True

    return False


def clean_export(customer, client_data):
    return customer[client_data.dear_is_export_field]


def clean_buyer_type(is_business):
    if is_business:
        return "0"
    else:
        return "1"


def clean_buyer_details(invoice_data, buyer_type, tax_pin):
    buyer_details = {
        "tax_pin": tax_pin,
        "nin": "",
        "passport_number": "",
        "legal_name": invoice_data["CompanyName"],
        "business_name": invoice_data["CompanyName"],
        "address": "",
        "email": invoice_data["Email"],
        "mobile": invoice_data["MobileNumber"],
        "buyer_type": buyer_type,
        "buyer_citizenship": "",
        "buyer_sector": "",
        "buyer_reference": invoice_data["Name"],
        "is_priviledged": False,
    }

    return buyer_details


def clean_goods_details(goods):
    goods_details = []
    for item in goods:
        good = item["FinProduct"]
        good = {
            "good_code": good["BaseItemCode"],
            "quantity": item["Quantity"],
            "sale_price": item["UnitSelling"],
        }

        goods_details.append(good)
    return goods_details


def create_efris_invoice(
    invoice_data,
    industry_code,
    buyer_details,
    cashier,
    goods_details,
    client_data,
    is_export,
    payment_mode="102",
    invoice_type="1",
    invoice_kind="1",
    credit_notes="",
):
    original_invoice_code = ""
    return_reason = ""
    return_reason_code = ""
    invoice_code = ""
    currency_code = clean_currency_product(
        invoice_data["ManualClient"]["FinClient"]["CurrencyCode"]
    )

    if credit_notes:
        pass
        # for new_credit_note in credit_notes:
        #     original_invoice_code = new_credit_note["CreditNoteInvoiceNumber"]
        #     invoice_code = new_credit_note["CreditNoteNumber"]
        #     return_reason = new_credit_note["TaskID"]
        #     return_reason_code = "102"
    else:
        invoice_code = invoice_data["ProjectId"]

    mita_payload = {
        "invoice_details": {
            "invoice_code": invoice_code,
            "cashier": cashier,
            "payment_mode": payment_mode,
            "currency": currency_code,
            "invoice_type": invoice_type,
            "invoice_kind": invoice_kind,
            "goods_description": invoice_data["Description"],
            "industry_code": industry_code,
            "original_instance_invoice_id": original_invoice_code,
            "return_reason": return_reason,
            "return_reason_code": return_reason_code,
            "is_export": is_export,
        },
        "goods_details": goods_details,
        "buyer_details": {
            "tax_pin": buyer_details["tax_pin"],
            "nin": "",
            "passport_number": "",
            "legal_name": buyer_details["legal_name"],
            "business_name": "",
            "address": "",
            "email": "",
            "mobile": "",
            "buyer_type": buyer_details["buyer_type"],
            "buyer_citizenship": "",
            "buyer_sector": "",
            "buyer_reference": "",
            "is_privileged": buyer_details["is_priviledged"],
            "local_purchase_order": "",
        },
        "instance_invoice_id": invoice_code,
    }
    struct_logger.info(event="sending dear invoice to mita", mita_payload=mita_payload)
    return send_mita_request("invoice/queue", mita_payload, client_data)


def create_goods_configuration(request, client_acc_id):
    # Get local client
    client_data = get_object_or_404(OEEfrisClientCredentials, pk=client_acc_id)
    try:
        struct_logger.info(
            event="create_oe_goods_configuration",
            product=request,
        )

        goods_name = request["Code"]
        goods_code = request["Code"]
        description = request["Description"]
        measure_unit = client_data.stock_configuration_measure_unit
        currency = client_data.stock_configuration_currency
        unit_price = client_data.stock_configuration_unit_price
        commodity_category = client_data.stock_configuration_commodity_category

        try:
            efris_key_values = request["FinProductKeyValues"]

            for efris_key in efris_key_values:
                for key, value in efris_key.items():
                    if value == "URA-MEASURE-UNIT":
                        measure_unit = efris_key["Value"]
                    elif value == "URA-COMMODITY-CATEGORY":
                        commodity_category = efris_key["Value"]
                    elif value == "CURRENCY":
                        currency = efris_key["Value"]
                    elif value == "UNIT-PRICE":
                        unit_price = efris_key["Value"]
                    else:
                        print(efris_key["Value"])
        except Exception as ex:
            pass
        efris_stock_configuration_payload = {
            "goods_name": goods_name,
            "goods_code": goods_code,
            "unit_price": unit_price,
            "measure_unit": measure_unit,
            "currency": currency,
            "commodity_tax_category": commodity_category,
            "goods_description": description,
        }

        struct_logger.info(
            event="create_dear_goods_configuration",
            efris_product=efris_stock_configuration_payload,
            message="sending dear goods configuration to mita",
        )
        efris_response = send_mita_request(
            "stock/configuration", efris_stock_configuration_payload, client_data
        )

        return HttpResponse(
            "xero Item saved {}  \n EFRIS Item Saved {} ".format("item", efris_response)
        )

    except Exception as ex:
        struct_logger.info(
            event="create_oe_goods_configuration",
            error=str(ex),
            message="Could not configure product from order east",
        )
        return {
            "request": request,
            "message": "Could not configure ordereazy product",
            "error": ex,
        }


def create_bulk_stock_configuration(client_acc_id):
    try:
        # no provision on the interface
        product_data = send_oe_api_request("product/list", client_acc_id)

        products = product_data["Data"]

        for product in products:
            configuration = create_goods_configuration(product, client_acc_id)

            struct_logger.info(
                event="create_oe_goods_configuration_bulk",
                product=product,
                response=configuration,
                message="Could not configure product from order east",
            )

        return True

    except Exception as ex:
        struct_logger.error(
            event="create_oe_goods_configuration_bulk",
            error=str(ex),
            message="Could not configure product from order east",
        )
