from django.shortcuts import get_object_or_404
import requests
import structlog

from intuitlib.client import AuthClient
from quickbooks import QuickBooks
from quickbooks.exceptions import QuickbooksException
from quickbooks.objects.invoice import Invoice

from .models import QuickbooksEfrisClientCredentials

#Backend client for intuit oauth
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

struct_logger = structlog.get_logger(__name__)

def setup_oauthlib_client(client_acc_id):
    try:

        # Get local client
        client_data = get_object_or_404(
            QuickbooksEfrisClientCredentials, pk=client_acc_id
        )
        client_id=client_data.client_id,
        client_secret=client_data.client_secret
        company_id = client_data.realm_id
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(
            token_url='https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
            client_id=client_id,
            client_secret=client_secret
        )
        access_token = token['access_token']
        
        return access_token, company_id

    except Exception as e:
        struct_logger.error(
            event="setup_oauthlib_client_quickbooks",
            message=e,
        )

        return None


def oauthlib_api_request(access_token, company_id):
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }

        # Example: Get the list of customers
        url = 'https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/query?query=SELECT%20%2A%20FROM%20Customer'
        response = requests.get(url, headers=headers)
        data = response.json()
        return data

    except Exception as ex:

        return str(ex)




def setup_auth_client(client_data):
    try:
        auth_client = AuthClient(
            client_id=client_data.client_id,
            client_secret=client_data.client_secret,
            access_token=client_data.access_token,  # If you do not pass this in, the Quickbooks client will call refresh and get a new access token.
            environment=client_data.environment,
            redirect_uri=client_data.callback_uri,
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


def setup_auth_client_token(client_data, state_token):
    try:
        auth_client = AuthClient(
            client_id=client_data.client_id,
            client_secret=client_data.client_secret,
            access_token=client_data.access_token,  # If you do not pass this in, the Quickbooks client will call refresh and get a new access token.
            environment=client_data.environment,
            redirect_uri=client_data.callback_uri,
            state_token=state_token,
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


def create_quickbooks_client(client_acc_id):
    try:
        # Get local client
        client_data = get_object_or_404(
            QuickbooksEfrisClientCredentials, pk=client_acc_id
        )

        auth_client = setup_auth_client(client_data)

        client = QuickBooks(
            auth_client=auth_client,
            refresh_token=client_data.refresh_token,
            company_id=client_data.quick_books_id,
        )

        return client

    except QuickbooksException as e:
        struct_logger.error(
            event="create_quickbooks_client",
            message=e.message,
            code=e.error_code,
            detail=e.detail,
        )

        return None


def get_invoice_by_id(client_acc_id, invoice_id):
    client = create_quickbooks_client(client_acc_id=client_acc_id)

    invoice = Invoice.get(invoice_id, qb=client)

    return invoice


def get_qb_company_info(access_token, realm_id, client_data):


    if client_data.environment == "production":
        base_url = client_data.prod_url
    else:
        base_url = client_data.sandbox_url

    route = "/v3/company/{0}/companyinfo/{0}".format(realm_id)
    auth_header = "Bearer {0}".format(access_token)
    headers = {"Authorization": auth_header, "Accept": "application/json"}
    return requests.get("{0}{1}".format(base_url, route), headers=headers)
