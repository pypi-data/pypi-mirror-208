import typing_extensions

from cashfree_lrs_client.paths import PathValues
from cashfree_lrs_client.apis.paths.orders import Orders
from cashfree_lrs_client.apis.paths.orders_order_id_process import OrdersOrderIdProcess
from cashfree_lrs_client.apis.paths.orders_order_id_documents_upload import OrdersOrderIdDocumentsUpload
from cashfree_lrs_client.apis.paths.fx_rate_details import FxRateDetails
from cashfree_lrs_client.apis.paths.webhooks import Webhooks
from cashfree_lrs_client.apis.paths.beneficiaries import Beneficiaries
from cashfree_lrs_client.apis.paths.remitters import Remitters
from cashfree_lrs_client.apis.paths.orders_documents_upload import OrdersDocumentsUpload

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.ORDERS: Orders,
        PathValues.ORDERS_ORDER_ID_PROCESS: OrdersOrderIdProcess,
        PathValues.ORDERS_ORDER_ID_DOCUMENTS_UPLOAD: OrdersOrderIdDocumentsUpload,
        PathValues.FXRATE_DETAILS: FxRateDetails,
        PathValues.WEBHOOKS: Webhooks,
        PathValues.BENEFICIARIES: Beneficiaries,
        PathValues.REMITTERS: Remitters,
        PathValues.ORDERS_DOCUMENTS_UPLOAD: OrdersDocumentsUpload,
    }
)

path_to_api = PathToApi(
    {
        PathValues.ORDERS: Orders,
        PathValues.ORDERS_ORDER_ID_PROCESS: OrdersOrderIdProcess,
        PathValues.ORDERS_ORDER_ID_DOCUMENTS_UPLOAD: OrdersOrderIdDocumentsUpload,
        PathValues.FXRATE_DETAILS: FxRateDetails,
        PathValues.WEBHOOKS: Webhooks,
        PathValues.BENEFICIARIES: Beneficiaries,
        PathValues.REMITTERS: Remitters,
        PathValues.ORDERS_DOCUMENTS_UPLOAD: OrdersDocumentsUpload,
    }
)
