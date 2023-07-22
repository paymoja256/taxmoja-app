import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt

import structlog

from intuitlib.client import AuthClient
from intuitlib.migration import migrate
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError

from .models import QuickbooksEfrisClientCredentials
from .services_old import (
    get_qb_company_info,
    oauthlib_api_request,
    setup_auth_client,
    setup_auth_client_token,
    setup_oauthlib_client,
)

struct_logger = structlog.get_logger(__name__)


@csrf_exempt
def webhook(request, client_acc_id):
    try:
        body_unicode = request.body.decode("utf-8")
        request = json.loads(body_unicode)

        response = ""

        signature = request.get("intuit-signature")

        if not signature:
            return HttpResponse(status=401)

        if not request:
            return HttpResponse(status=200)

        # mita_invoice = process_invoice(request, client_acc_id)

        struct_logger.info(
            event="quickbooks webhook", request=request, response="mita_invoice"
        )

        return HttpResponse(status=200)
    except Exception as ex:
        struct_logger.error(event="quickbooks webhook", error=str(ex))

        return HttpResponse(status=500)


@csrf_exempt
def oauth(request, client_acc_id):
    try:
        client_data = get_object_or_404(
            QuickbooksEfrisClientCredentials, pk=client_acc_id
        )

        auth_client = setup_auth_client(client_data)

        url = auth_client.get_authorization_url([Scopes.ACCOUNTING])

        struct_logger.info(event="quickbooks oauth", redirect_url=url)

        request.session["state"] = auth_client.state_token

        return redirect(url)
    except Exception as ex:
        struct_logger.error(event="quickbooks oauth", error=str(ex))

        return HttpResponse(status=500)


@csrf_exempt
def oauth2(request, client_acc_id):
    try:

        access_token, company_id= setup_oauthlib_client(client_acc_id)

        request =  oauthlib_api_request(access_token, company_id)

        struct_logger.info(event="quickbooks oauthlib", request=request)

        return HttpResponse(status=200)
    except Exception as ex:
        struct_logger.error(event="quickbooks oauthlib", error=str(ex))

        return HttpResponse(status=500)


def openid(request, client_acc_id):
    client_data = get_object_or_404(QuickbooksEfrisClientCredentials, pk=client_acc_id)

    auth_client = setup_auth_client(client_data)

    url = auth_client.get_authorization_url([Scopes.OPENID, Scopes.EMAIL])
    request.session["state"] = auth_client.state_token
    return redirect(url)


def callback(request, client_acc_id):
    client_data = get_object_or_404(QuickbooksEfrisClientCredentials, pk=client_acc_id)

    struct_logger.info(event="quickbooks callback", request=request)

    state_token = request.GET.get("state", None)

    auth_client = setup_auth_client_token(client_data, state_token)
    state_tok = request.GET.get("state", None)
    error = request.GET.get("error", None)

    if error == "access_denied":
        print("access denied")

    if state_tok is None:
        return HttpResponseBadRequest()
    elif state_tok != auth_client.state_token:
        return HttpResponse("unauthorized", status=401)

    auth_code = request.GET.get("code", None)
    realm_id = request.GET.get("realmId", None)
    request.session["realm_id"] = realm_id

    if auth_code is None:
        return HttpResponseBadRequest()

    try:
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        request.session["access_token"] = auth_client.access_token
        request.session["refresh_token"] = auth_client.refresh_token
        request.session["id_token"] = auth_client.id_token

        client_data.access_token = auth_client.access_token
        client_data.refresh_token = auth_client.refresh_token
        client_data.realm_id = auth_client.id_token

        client_data.save()

        return HttpResponse("You are authenticated")
    except AuthClientError as e:
        # just printing status_code here but it can be used for retry workflows, etc
        print(e.status_code)
        print(e.content)
        print(e.intuit_tid)

        return HttpResponse(
            "Authclient Error: status code: {} - content: {} - intuit_tid: {}".format(
                e.status_code, e.content, e.intuit_tid
            )
        )
    except Exception as e:
        return HttpResponse("Authclient Error: status code: {}".format(e))


def connected(request, client_acc_id):
    struct_logger.info(event="quickbooks connected", request=request)
    client_data = get_object_or_404(QuickbooksEfrisClientCredentials, pk=client_acc_id)
    auth_client = AuthClient(
        client_id=client_data.client_id,
        client_secret=client_data.client_secret,
        environment=client_data.environment,
        redirect_uri=client_data.callback_uri,
        access_token=request.session.get("access_token", None),
        refresh_token=request.session.get("refresh_token", None),
        id_token=request.session.get("id_token", None),
    )

    if auth_client.id_token is not None:
        return HttpResponse(
            "You are authenticated. Token:{}".format(auth_client.id_token)
        )

    else:
        return HttpResponse("You are not authenticated")


def qbo_company_info_request(request, client_acc_id):
    client_data = get_object_or_404(QuickbooksEfrisClientCredentials, pk=client_acc_id)
    auth_client = AuthClient(
        client_id=client_data.client_id,
        client_secret=client_data.client_secret,
        environment=client_data.environment,
        redirect_uri=client_data.callback_uri,
        access_token=client_data.access_token,
        refresh_token=client_data.refresh_token,
        realm_id=client_data.realm_id,
    )

    if auth_client.access_token is not None:
        access_token = auth_client.access_token

    if auth_client.realm_id is None:
        raise ValueError("Realm id not specified.")
    response = get_qb_company_info(
        auth_client.access_token, auth_client.realm_id, client_data
    )

    if not response.ok:
        return HttpResponse(" ".join([response.content, str(response.status_code)]))
    else:
        return HttpResponse(response.content)


def user_info(request, client_acc_id):
    client_data = get_object_or_404(QuickbooksEfrisClientCredentials, pk=client_acc_id)
    auth_client = AuthClient(
        client_id=client_data.client_id,
        client_secret=client_data.client_secret,
        environment=client_data.environment,
        redirect_uri=client_data.callback_uri,
        access_token=client_data.access_token,
        refresh_token=client_data.refresh_token,
        id_token=request.session.get("id_token", None),
    )

    try:
        response = auth_client.get_user_info()
    except ValueError:
        return HttpResponse("id_token or access_token not found.")
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse(response.content)


def refresh(request, client_acc_id):
    client_data = get_object_or_404(QuickbooksEfrisClientCredentials, pk=client_acc_id)
    auth_client = AuthClient(
        client_id=client_data.client_id,
        client_secret=client_data.client_secret,
        environment=client_data.environment,
        redirect_uri=client_data.callback_uri,
        access_token=client_data.access_token,
        refresh_token=client_data.refresh_token,
    )

    try:
        auth_client.refresh()
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse("New refresh_token: {0}".format(auth_client.refresh_token))


def revoke(request, client_acc_id):
    client_data = get_object_or_404(QuickbooksEfrisClientCredentials, pk=client_acc_id)
    auth_client = AuthClient(
        client_id=client_data.client_id,
        client_secret=client_data.client_secret,
        environment=client_data.environment,
        redirect_uri=client_data.callback_uri,
        access_token=request.session.get("access_token", None),
        refresh_token=request.session.get("refresh_token", None),
    )
    try:
        is_revoked = auth_client.revoke()
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse("Revoke successful")
