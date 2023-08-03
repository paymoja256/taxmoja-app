from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
import requests
import structlog
import json

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks.exceptions import QuickbooksException
from requests.auth import HTTPBasicAuth
from api_mita.services import send_mita_request


struct_logger = structlog.get_logger(__name__)
# Processing webhook


def process_webhook(request, client_data):
    notifications = request["eventNotifications"]

    for notification in notifications:
        event = notification["dataChangeEvent"]["entities"][0]
        event_name = event["name"]
        event_id = event["id"]
        operation = event["operation"].lower()
        process_name = event_name.lower()
        event_process = globals()["process_{}".format(process_name)]

        response = event_process(event_id, operation, client_data)

        struct_logger.info(
            event="quickbooks process webhook",
            process_name=process_name,
            response=response,
        )

        return response


#  Helper functions for webhook


# Invoicing
def process_invoice(id, operation, client_data):
    item_data = json.loads(get_invoice_by_id(client_data, id))["Invoice"]

    struct_logger.info(
        event="fetching invoice from quickbooks",
        invoice=item_data,
    )

    if operation == "create":
        mita_response = create_efris_invoice(item_data, client_data)
    elif operation == "update":
        mita_response = create_efris_invoice(item_data, client_data)

    struct_logger.info(
        event="quickbooks process invoice",
        mita_response=mita_response.text,
        item_data=item_data,
    )

    return mita_response.text


def get_invoice_by_id(client_data, item_id):
    route = "invoice/{}".format(item_id)

    response = quickbooks_api_request("GET", client_data, route)

    return response


def get_customer_by_id(client_data, item_id):
    route = "customer/{}".format(item_id)

    response = quickbooks_api_request("GET", client_data, route)

    return response


# Efris Invoice


def create_efris_invoice(
    invoice_data,
    client_data,
    is_export=False,
    industry_code="101",
    payment_mode="102",
    invoice_type="1",
    invoice_kind="1",
    credit_notes="",
):
    original_invoice_code = ""
    return_reason = ""
    return_reason_code = ""
    invoice_code = ""

    if credit_notes:
        pass
        # for new_credit_note in credit_notes:
        #     original_invoice_code = new_credit_note["CreditNoteInvoiceNumber"]
        #     invoice_code = new_credit_note["CreditNoteNumber"]
        #     return_reason = new_credit_note["TaskID"]
        #     return_reason_code = "102"
    else:
        invoice_code = invoice_data["Id"]
        cashier = client_data.cashier
        buyer_details = get_customer_by_id(
            client_data, invoice_data["CustomerRef"]["value"]
        )

        buyer_details = json.loads(buyer_details)["Customer"]

        goods_details = clean_goods_details(invoice_data)

        currency = invoice_data["CurrencyRef"]["value"]
        description = "{}-{}".format(invoice_data["CustomerMemo"], invoice_data["Id"])

        if is_export:
            industry_code = "102"

    is_privileged = not buyer_details["Taxable"]

    buyer_type, buyer_name = clean_buyer_type(buyer_details)

    tax_pin = ""

    mita_payload = {
        "invoice_details": {
            "invoice_code": invoice_code,
            "cashier": cashier,
            "payment_mode": payment_mode,
            "currency": currency,
            "invoice_type": invoice_type,
            "invoice_kind": invoice_kind,
            "goods_description": description,
            "industry_code": industry_code,
            "original_instance_invoice_id": original_invoice_code,
            "return_reason": return_reason,
            "return_reason_code": return_reason_code,
            "is_export": is_export,
        },
        "goods_details": goods_details,
        "buyer_details": {
            "tax_pin": tax_pin,
            "nin": "",
            "passport_number": "",
            "legal_name": buyer_name,
            "business_name": "",
            "address": "",
            "email": "",
            "mobile": "",
            "buyer_type": buyer_type,
            "buyer_citizenship": "",
            "buyer_sector": "",
            "buyer_reference": "",
            "is_privileged": is_privileged,
            "local_purchase_order": "",
        },
        "instance_invoice_id": invoice_code,
    }
    struct_logger.info(event="sending dear invoice to mita", mita_payload=mita_payload)
    return send_mita_request("invoice/queue", mita_payload, client_data)


def clean_goods_details(invoice):
    goods = invoice["Line"]
    goods_details = []
    for item in goods:
        try:
            item_details = item["SalesItemLineDetail"]
            good = {
                "good_code": item_details["ItemRef"]["value"],
                "quantity": item_details["Qty"],
                "sale_price": item_details["UnitPrice"],
            }

            goods_details.append(good)
        except Exception as ex:
            pass

    struct_logger.info(event="quickbooks clean_goods_details", goods=goods_details)
    return goods_details


def get_tax_rate(tax_rule):
    if tax_rule.upper() == "VAT":
        return True

    return False


def clean_buyer_type(buyer_details):

    
    if buyer_details["CompanyName"]:
        return "1", buyer_details["CompanyName"]

    return "1", buyer_details["DisplayName"]


# Stock
def process_item(id, operation, client_data):
    item_data = get_item_by_id(client_data, id)
    product_data = json.loads(item_data)["Item"]
    if operation == "create":
        mita_response = create_goods_configuration(product_data, client_data)
    elif operation == "update":
        mita_response = create_goods_configuration(product_data, client_data)

    struct_logger.info(
        event="quickbooks process item",
        mita_response=mita_response.text,
        item_data=product_data,
    )

    return mita_response.text


def create_bulk_stock_configuration(client_data):
    try:
        # no provision on the interface
        product_data = json.loads(get_all_items(client_data))

        products = product_data["QueryResponse"]["Item"]

        for product in products:
            mita_response = create_goods_configuration(product, client_data)

        struct_logger.info(
            event="quickbooks process item",
            mita_response=mita_response,
            item_data=product,
        )
        return True

    except Exception as ex:
        struct_logger.error(
            event="create_items_goods_configuration_bulk",
            error=str(ex),
            message="Could not configure product from quickbooks",
        )


def get_item_by_id(client_data, item_id):
    route = "item/{}".format(item_id)

    response = quickbooks_api_request("GET", client_data, route)

    struct_logger.info(
        event="quickbooks get_item_by_id",
        qb_response=response,
        item_data=item_id,
    )

    return response


def get_all_items(client_data):
    route = "query?query=select * from Item"
    response = quickbooks_api_request("GET", client_data, route)

    struct_logger.info(
        event="quickbooks get_all_items",
        qb_response=response,
    )

    return response


#  EFRIS Stock


def create_goods_configuration(product_data, client_data):
    # Get local client

    try:
        struct_logger.info(
            event="create_quickbooks_goods_configuration",
            quickbooks_item=product_data,
            message="new item received from quickbooks",
        )
        try:
            goods_name = product_data["Name"]
            goods_code = product_data["Id"]
            unit_price = product_data["UnitPrice"]
            description = product_data["Description"]
        except Exception as ex:

            goods_name = product_data["Name"]
            goods_code = product_data["Id"]
            unit_price = '1.0'
            description = product_data["FullyQualifiedName"]

        measure_unit = client_data.stock_configuration_measure_unit
        currency = client_data.stock_configuration_currency
        commodity_category = client_data.stock_configuration_commodity_category

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
            event="create_quickbooks_goods_configuration",
            efris_product=efris_stock_configuration_payload,
            message="sending quickbooks goods configuration to mita",
        )
        efris_response = send_mita_request(
            "stock/configuration", efris_stock_configuration_payload, client_data
        )

        return efris_response
    except Exception as ex:
        struct_logger.info(
            event="create_quickbooks_goods_configuration",
            error=str(ex),
            message="Could not configure product",
        )
        return {
            "message": "Could not configure product: {}".format(product_data),
            "error": ex,
        }


# Company test
def get_company_info(client_data):
    route = "companyinfo/{0}".format(client_data.realm_id)

    response = quickbooks_api_request("GET", client_data, route)

    return response


# Request flow


# Authorisation flow: These help authenticate the app
# Get authorization code
def get_authorisation_code(client_data):
    auth_client = setup_auth_client(client_data)

    scopes = [
        Scopes.ACCOUNTING,
    ]

    auth_url = auth_client.get_authorization_url(scopes)

    struct_logger.info(event="get_authorisation_code", url=auth_url)

    return auth_url


# Get OAuth 2.0 token from auth code
def get_access_tokens(client_data):
    auth_client = setup_auth_client(client_data)
    auth_client.get_bearer_token(client_data.auth_code, realm_id=client_data.realm_id)

    struct_logger.info(
        event="quickbooks get_access_tokens",
        access_token=auth_client.access_token,
        refresh_token=auth_client.refresh_token,
    )

    return auth_client


def refresh_token(client_data):
    auth_client = setup_auth_client(client_data)

    auth_client.refresh(refresh_token=client_data.refresh_token)

    struct_logger.info(event="quickbooks token refresh service", token_expiry="")

    return auth_client


def refresh_token_request(client_data):
    try:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": client_data.refresh_token,
        }

        base_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

        response = connect_to_app_center(client_data, base_url, data)

        client_data.cred_state = response

        client_data.save()

        return response
    except Exception as ex:
        return None


def revoke_token(client_data):
    auth_client = setup_auth_client(client_data)

    auth_client.revoke(token=client_data.access_token)

    struct_logger.info(
        event="quickbooks revoke token service", token=auth_client.access_token
    )

    return auth_client


def setup_auth_client(client_data):
    try:
        auth_client = AuthClient(
            client_data.client_id,
            client_data.client_secret,
            client_data.callback_uri,
            client_data.environment,  # “sandbox” or “production”
        )

        return auth_client

    except QuickbooksException as e:
        struct_logger.error(
            event="setup_auth_client_quickbooks",
            message=e.message,
            code=e.error_code,
            detail=e.detail,
        )

        return None


# API requests


def quickbooks_api_request(
    request_method, client_data, route, payload={}, authorisation_basic=False
):
    if client_data.environment == "production":
        base_url = client_data.prod_url
    else:
        base_url = client_data.sandbox_url

    auth_header = "Bearer {0}".format(client_data.access_token)
    if authorisation_basic:
        auth_header = "Basic {0}".format(client_data.basic_token)

    headers = {"Authorization": auth_header, "Accept": "application/json"}

    request_url = "{0}/{1}/{2}".format(base_url, client_data.realm_id, route)

    response = requests.request(
        request_method, request_url, headers=headers, data=payload
    )

    struct_logger.info(
        event="quickbooks_api_request", url=request_url, response=response.text
    )

    return response.text


def connect_to_app_center(client_data, request_uri, data={}):
    auth_token = HTTPBasicAuth(
        "{}".format(client_data.client_id), "{}".format(client_data.client_secret)
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic {}".format(auth_token),
    }

    struct_logger.info(
        event="quickbooks_connect_to_app_center",
        url=request_uri,
        headers=headers,
        data=data,
    )

    response = requests.post(request_uri, auth=auth_token, headers=headers, data=data)

    return response.text
