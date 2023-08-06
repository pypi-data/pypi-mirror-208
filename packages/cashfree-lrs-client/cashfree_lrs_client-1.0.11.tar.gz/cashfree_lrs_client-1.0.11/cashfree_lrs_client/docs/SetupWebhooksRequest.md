# SetupWebhooksRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_url** | **str** | Specify the URL where you want to receive information about payments. | 
**refund_url** | **str** | Specify the URL where you want to receive information about refunds. | 
**order_url** | **str** | Specify the URL where you want to receive information about orders. | 

## Example

```python
from cashfree_lrs_client.models.setup_webhooks_request import SetupWebhooksRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SetupWebhooksRequest from a JSON string
setup_webhooks_request_instance = SetupWebhooksRequest.from_json(json)
# print the JSON string representation of the object
print SetupWebhooksRequest.to_json()

# convert the object into a dict
setup_webhooks_request_dict = setup_webhooks_request_instance.to_dict()
# create an instance of SetupWebhooksRequest from a dict
setup_webhooks_request_form_dict = setup_webhooks_request.from_dict(setup_webhooks_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


