import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt

import structlog
from . import services, models

from intuitlib.exceptions import AuthClientError


struct_logger = structlog.get_logger(__name__)


@csrf_exempt
def webhook(request, client_acc_id):
    try:
        client_data = get_object_or_404(
            models.QuickbooksEfrisClientCredentials, pk=client_acc_id
        )
        body_unicode = request.body.decode("utf-8")
        request_body = json.loads(body_unicode)
        signature = request.headers["Intuit-Signature"]
        struct_logger.info(
            event="quickbooks webhook",
            request=request_body,
            headers=request.headers,
            signature=signature,
        )

        if not signature:
            return HttpResponse(status=401)

        if not request:
            return HttpResponse(status=200)

        response = oauth2(request, client_acc_id)
        struct_logger.info(
            event="oauth2",
            response=response,
            item="refreshing access token",
        )

        mita_response = services.process_webhook(request_body, client_data)

        struct_logger.info(
            event="quickbooks webhook", response=mita_response, item=request_body
        )

        return HttpResponse(status=200, content=mita_response)
    except Exception as ex:
        struct_logger.error(event="quickbooks webhook", error=str(ex))

        return HttpResponse(status=500)


@csrf_exempt
def refresh(request, client_acc_id):
    try:
        client_data = get_object_or_404(
            models.QuickbooksEfrisClientCredentials, pk=client_acc_id
        )

        response = services.refresh_token_request(client_data)

        struct_logger.info(
            event="quickbooks refresh token", message="success", response=response
        )

        return HttpResponse(status=200, content=response)

    except Exception as ex:
        struct_logger.error(event="quickbooks refresh token", error=str(ex))

        return HttpResponse(status=500)


@csrf_exempt
def revoke(request, client_acc_id):
    try:
        client_data = get_object_or_404(
            models.QuickbooksEfrisClientCredentials, pk=client_acc_id
        )

        response = services.revoke_token(client_data)

        struct_logger.info(
            event="quickbooks refresh token", message="success", response=response
        )

        return HttpResponse(status=200)

    except Exception as ex:
        struct_logger.error(event="quickbooks refresh token", error=str(ex))

        return HttpResponse(status=500)


@csrf_exempt
def oauth2(request, client_acc_id):
    try:
        client_data = get_object_or_404(
            models.QuickbooksEfrisClientCredentials, pk=client_acc_id
        )

        auth_url = services.get_authorisation_code(client_data)

        struct_logger.info(
            event="quickbooks oauth2_authentication",
            message="success",
            redirect_url=auth_url,
        )

        return redirect(auth_url)

    except Exception as ex:
        struct_logger.error(event="quickbooks oauth2_authentication", error=str(ex))

        return HttpResponse(status=500)


@csrf_exempt
def callback(request, client_acc_id):
    try:
        client_data = get_object_or_404(
            models.QuickbooksEfrisClientCredentials, pk=client_acc_id
        )

        struct_logger.info(event="quickbooks callback", request=request.body)

        state_token = request.GET.get("state", None)
        authorisation_code = request.GET.get("code", None)

        client_data.state = state_token

        client_data.auth_code = authorisation_code

        client_data.save()

        struct_logger.info(
            event="quickbooks callback view",
            message="saving authorisation code",
            client_data=client_data.auth_code,
            code=authorisation_code,
            state=state_token,
        )

        auth_client = services.get_access_tokens(client_data)

        client_data.access_token = auth_client.access_token
        client_data.refresh_token = auth_client.refresh_token

        client_data.save()

        struct_logger.info(
            event="quickbooks callback view",
            message="saving tokens to database",
            access_token=auth_client.access_token,
            refresh_token=auth_client.refresh_token,
            db_access_token=client_data.access_token,
            db_refresh_token=client_data.refresh_token,
        )

        return HttpResponse(
            "Authorisation code has been saved:: {}".format(authorisation_code)
        )

    except Exception as e:
        return HttpResponse("Authclient Error: status code: {}".format(e))


@csrf_exempt
def company_info(request, client_acc_id):
    try:
        client_data = get_object_or_404(
            models.QuickbooksEfrisClientCredentials, pk=client_acc_id
        )

        services.refresh_token(client_data)

        response = services.get_company_info(client_data)

        struct_logger.info(
            event="quickbooks test client info", message="success", response=response
        )

        return HttpResponse("Client data retrieved: {}".format(response))
    except Exception as ex:
        struct_logger.error(event="quickbooks refresh token", error=str(ex))

        return HttpResponse(status=500)


@csrf_exempt
def stock_configuration_bulk_webhook(request, client_acc_id):
    try:
        client_data = get_object_or_404(
            models.QuickbooksEfrisClientCredentials, pk=client_acc_id
        )

        goods_configuration = services.create_bulk_stock_configuration(client_data)

        struct_logger.info(
            event="processing quickbooks bulk goods configuration", response=goods_configuration
        )

        return HttpResponse(status=200)
    except Exception as ex:
        struct_logger.error(event="processing quickbooks bulk goods configuration", error=str(ex))
        return HttpResponse(status=500)
