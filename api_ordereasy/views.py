import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api_mita.services import send_mita_request
from .services import (
    create_bulk_stock_configuration,
    create_goods_configuration,
    process_credit_note,
    process_invoice,
)

import structlog

struct_logger = structlog.get_logger(__name__)


@csrf_exempt
def invoice_webhook(request, client_acc_id):
    try:
        body_unicode = request.body.decode("utf-8")
        request = json.loads(body_unicode)

        mita_invoice = process_invoice(request, client_acc_id)

        struct_logger.info(
            event="processing oe invoice", request=request, response=request
        )

        return HttpResponse(status=200)
    except Exception as ex:
        struct_logger.error(event="processing oe invoice", error=str(ex))

        return HttpResponse(status=500)


@csrf_exempt
def creditnote_webhook(request, client_acc_id):
    try:
        body_unicode = request.body.decode("utf-8")
        request = json.loads(body_unicode)

        # mita_invoice = process_credit_note(request, client_acc_id)

        struct_logger.info(event="processing oe creditnote", response=request)

        return HttpResponse(status=200)
    except Exception as ex:
        struct_logger.error(event="processing oe creditnote", error=str(ex))
        return HttpResponse(status=500)


@csrf_exempt
def stock_configuration_webhook(request, client_acc_id):
    try:
        body_unicode = request.body.decode("utf-8")
        request = json.loads(body_unicode)

        goods_configuration = create_goods_configuration(request, client_acc_id)

        struct_logger.info(
            event="processing oe goods configuration", response=goods_configuration
        )

        return HttpResponse(status=200)
    except Exception as ex:
        struct_logger.error(event="processing oe goods configuration", error=str(ex))
        return HttpResponse(status=500)


@csrf_exempt
def stock_adjustment_webhook(request, client_acc_id):
    try:
        body_unicode = request.body.decode("utf-8")
        request = json.loads(body_unicode)

        struct_logger.info(event="processing oe stock adjustment", stock=request)

        # goods_configuration = create_goods_adjustment(request, client_acc_id)

        # struct_logger.info(event="processing dear goods adjustment", response=goods_configuration)

        return HttpResponse(status=200)
    except Exception as ex:
        struct_logger.error(event="processing oe goods adjustment", error=str(ex))
        return HttpResponse(status=500)


@csrf_exempt
def stock_configuration_bulk_webhook(request, client_acc_id):
    try:

        goods_configuration = create_bulk_stock_configuration(client_acc_id)

        struct_logger.info(
            event="processing oe goods configuration", response=goods_configuration
        )

        return HttpResponse(status=200)
    except Exception as ex:
        struct_logger.error(event="processing oe goods configuration", error=str(ex))
        return HttpResponse(status=500)