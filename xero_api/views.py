import base64
import hashlib
import hmac
from http import client

from urllib.parse import urlparse
from urllib.parse import parse_qs

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.cache import caches, cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from xero import Xero
from xero.auth import OAuth2Credentials
from xero.constants import XeroScopes
from .models import ClientCredentials
from .services import get_xero_client_data, xero_send_invoice_data
 
from django.core.exceptions import BadRequest

import structlog

struct_logger = structlog.get_logger(__name__)


@csrf_exempt
def xero_invoice_webhook(request, client_acc_id):
    try:

        request_data = request.body
        client_data = get_xero_client_data(client_acc_id)
        header_signature = request.headers['X-Xero-Signature']
        webhook_key = client_data.webhook_key

        struct_logger.info(event="xero_invoice_webhook", client_account_id=client_acc_id)

        payload_hashed = hmac.new(bytes(webhook_key, 'utf8'),
                                  request_data, hashlib.sha256)
        generated_signature = base64.b64encode(
            payload_hashed.digest()).decode('utf8')

        struct_logger.info(event="xero_invoice_webhook",
                           payload_signature=generated_signature,
                           header_signature=header_signature,
                           data=request_data
                           )
        status_code = 401

        if header_signature == generated_signature:
            xero_send_invoice_data(request.body,  client_data)
            status_code = 200

        return HttpResponse(status=status_code)
    except Exception as ex:
        struct_logger.info(event="xero_invoice_webhook",
                           error=str(ex)
                           )
        return HttpResponse(status=401)


def start_xero_auth_view(request, client_acc_id):
    client_data = get_xero_client_data(client_acc_id)
    client_id = client_data.client_id
    client_secret = client_data.client_secret
    callback_uri = client_data.callback_uri

    credentials = OAuth2Credentials(
        client_id, client_secret, callback_uri=callback_uri,
        scope=[XeroScopes.OFFLINE_ACCESS,
               XeroScopes.ACCOUNTING_TRANSACTIONS, XeroScopes.ACCOUNTING_CONTACTS, XeroScopes.ACCOUNTING_SETTINGS]
    )

    authorization_url = credentials.generate_url()
    client_data.cred_state = credentials.state
    client_data.save()
    struct_logger.info(event='start_xero_auth_view', client_data=client_data.company_name, message='success')
    return HttpResponseRedirect(authorization_url)

def process_callback_view(request, client_acc_id):
    client_data = get_xero_client_data(client_acc_id)
    cred_state = client_data.cred_state
    credentials = OAuth2Credentials(**cred_state)
    auth_secret = request.build_absolute_uri()
    if "http:" in auth_secret:
        auth_secret = "https:" + auth_secret[5:]
    credentials.verify(auth_secret)
    credentials.set_default_tenant()
    client_data.cred_state = credentials.state
    client_data.save()
    return HttpResponse("You are authenticated")

