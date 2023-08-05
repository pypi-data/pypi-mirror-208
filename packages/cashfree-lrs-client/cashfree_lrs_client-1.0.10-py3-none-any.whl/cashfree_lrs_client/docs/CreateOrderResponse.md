# CreateOrderResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tcs** | **float** |  | [optional] 
**gst** | **float** |  | [optional] 
**fx_rate** | **float** |  | [optional] 
**amount_to_pay** | **float** |  | [optional] 
**handling_charges** | **float** |  | [optional] 
**order_expiry_time** | **datetime** |  | [optional] 
**payment_link** | **str** |  | [optional] 
**order_token** | **str** |  | [optional] 
**missing_documents** | **List[str]** |  | [optional] 

## Example

```python
from cashfree_lrs_client.models.create_order_response import CreateOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResponse from a JSON string
create_order_response_instance = CreateOrderResponse.from_json(json)
# print the JSON string representation of the object
print CreateOrderResponse.to_json()

# convert the object into a dict
create_order_response_dict = create_order_response_instance.to_dict()
# create an instance of CreateOrderResponse from a dict
create_order_response_form_dict = create_order_response.from_dict(create_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


