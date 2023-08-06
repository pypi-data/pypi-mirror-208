# CreateOrderRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_id** | **str** | Unique Order Id to place the order. Alphanumeric characters, hyphens and underscores are allowed. Maximum of 50 characters is allowed. | 
**to_currency** | [**Currency**](Currency.md) |  | 
**to_amount** | **float** | Final settlement amount in to_currency (Double with 2 decimals allowed) | 
**from_amount** | **float** | Amount in INR excluding GST, TCS and handling charges (Double with 2 decimals allowed) | [optional] 
**purpose** | [**Purpose**](Purpose.md) |  | 
**return_url** | **str** | The URL to which customer will be redirected to after the payment (should accept query params cf_id and cf_token). | 
**remitter_id** | **str** | Unique remitter ID to identify the remitter. Alphanumeric characters, hyphens, and underscores are allowed. Maximum of 50 characters are allowed. | 
**beneficiary_id** | **str** | Unique Beneficiary ID to identify the beneficiary. Alphanumeric characters and underscores are allowed. Maximum of 50 characters is allowed. | 
**customer_declaration** | **str** | Amount in INR declared by Customer (Double with 2 decimals allowed) | [optional] 
**doc_ids** | **str** | Comma seperated bulk_doc_id provided from the upload APIs. | [optional] 
**customer_relationship** | **str** |  | 
**education_loan** | **bool** | Whether the remitter has availed an education loan | [optional] [default to False]
**remarks** | **str** | Student ID? | [optional] 

## Example

```python
from cashfree_lrs_client.models.create_order_request import CreateOrderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderRequest from a JSON string
create_order_request_instance = CreateOrderRequest.from_json(json)
# print the JSON string representation of the object
print CreateOrderRequest.to_json()

# convert the object into a dict
create_order_request_dict = create_order_request_instance.to_dict()
# create an instance of CreateOrderRequest from a dict
create_order_request_form_dict = create_order_request.from_dict(create_order_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


