# FetchForexRateRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**to_currency** | [**Currency**](Currency.md) |  | 
**to_amount** | **float** | Final settlement amount in to_currency (Double with 2 decimals are allowed.) | 
**purpose** | [**Purpose**](Purpose.md) |  | 
**remitter_id** | **str** | Unique remitter ID to identify the remitter. Alphanumeric characters, hyphens, and underscores are allowed. Maximum of 50 characters are allowed. If remitter ID is not specificed the tcs value calculated is zero. | [optional] 
**customer_declaration** | **float** | Amount in INR declared by Customer (Double with 2 decimals are allowed.) | [optional] 
**education_loan** | **bool** | Whether user has availed an education loan | [optional] [default to False]

## Example

```python
from cashfree_lrs_client.models.fetch_forex_rate_request import FetchForexRateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FetchForexRateRequest from a JSON string
fetch_forex_rate_request_instance = FetchForexRateRequest.from_json(json)
# print the JSON string representation of the object
print FetchForexRateRequest.to_json()

# convert the object into a dict
fetch_forex_rate_request_dict = fetch_forex_rate_request_instance.to_dict()
# create an instance of FetchForexRateRequest from a dict
fetch_forex_rate_request_form_dict = fetch_forex_rate_request.from_dict(fetch_forex_rate_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


