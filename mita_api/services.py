import json
import requests
import structlog

from mita_api.models import MitaCredentials

struct_logger = structlog.get_logger(__name__)


def send_mita_request(url_ext, payload, client_account):
    mita_credentials=   MitaCredentials.objects.filter(active=True).first()
    
    struct_logger.info(event="send_mita_request", url_ext=url_ext, payload=payload, client_account=client_account)
    mita_url = mita_credentials.mita_url
    url = "{}/{}".format(mita_url,url_ext)
    headers = {
        'x-tax-id': '{}'.format(client_account.tax_pin),
        'x-api-token': '{}'.format(client_account.tax_pin),
        'x-tax-country-code': '{}'.format(client_account.mita_country_code),
        'x-api-key-header': '{}'.format(client_account.mita_api_header),
        'Content-Type': 'application/json'
    }

    payload = json.dumps(payload)

    response = requests.request("POST", url, headers=headers, data=payload)

    struct_logger.info(event='send_mita_request', payload=payload, response=response.text,
                       msg='Retrieving account client data')

    return response
