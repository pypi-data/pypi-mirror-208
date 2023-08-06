# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from cashfree_lrs_client.apis.path_to_api import path_to_api

import enum


class PathValues(str, enum.Enum):
    ORDERS = "/orders"
    ORDERS_ORDER_ID_PROCESS = "/orders/{order_id}/process"
    ORDERS_ORDER_ID_DOCUMENTS_UPLOAD = "/orders/{order_id}/documents/upload"
    FXRATE_DETAILS = "/fx-rate/details"
    WEBHOOKS = "/webhooks"
    BENEFICIARIES = "/beneficiaries"
    REMITTERS = "/remitters"
    ORDERS_DOCUMENTS_UPLOAD = "/orders/documents/upload"
