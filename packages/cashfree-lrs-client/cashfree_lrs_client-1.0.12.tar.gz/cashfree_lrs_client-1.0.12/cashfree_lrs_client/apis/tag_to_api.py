import typing_extensions

from cashfree_lrs_client.apis.tags import TagValues
from cashfree_lrs_client.apis.tags.lrs_api import LrsApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.LRS: LrsApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.LRS: LrsApi,
    }
)
