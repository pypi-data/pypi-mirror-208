# CreateRemitterRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**remitter_id** | **str** | Unique remitter ID to identify the remitter. Alphanumeric characters, hyphens, and underscores are allowed. Maximum of 50 characters are allowed. | 
**purpose** | [**Purpose**](Purpose.md) |  | 
**account_number** | **str** | Bank account number of the remitter. | 
**ifsc** | **str** | The IFSC information of the remitter bank account. It should be an alphanumeric value of 11 characters. The first 4 characters should be alphabets, the 5th character should be a 0, and the remaining 6 characters should be numerals. | 
**pan** | **str** | PAN of the remitter. Should include 10 characters. The first 5 characters are alphabets followed by 4 numbers and the 10th character is an alphabet. | 
**name** | **str** | Name of the remitter. Alphabets and spaces are allowed. | 
**address** | **str** | Address of the remitter. Alphanumeric charcaters, dot, and hyphens are allowed. | 
**city** | **str** | City of the remitter. Alphabets are only allowed. | 
**state** | **str** | State of the remitter. Alphabets are only allowed. | 
**postal_code** | **str** | Postal code of the remitter address. Numeric characters only allowed. | 
**phone_number** | **str** | Phone number of the remitter. Only numbers and hyphens are allowed. | [optional] 
**email** | **str** | Email address of the remitter. Example, abc@gmail.com | [optional] 
**nationality** | **str** | Nationality of the remitter. Only 2 alphabets are allowed. Example, IN for India. | 
**bank_code** | **str** | Remitter bank code. Required for net banking payments to perform bank account checks (TPV). Maximum of 4 characters allowed. | 

## Example

```python
from cashfree_lrs_client.models.create_remitter_request import CreateRemitterRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateRemitterRequest from a JSON string
create_remitter_request_instance = CreateRemitterRequest.from_json(json)
# print the JSON string representation of the object
print CreateRemitterRequest.to_json()

# convert the object into a dict
create_remitter_request_dict = create_remitter_request_instance.to_dict()
# create an instance of CreateRemitterRequest from a dict
create_remitter_request_form_dict = create_remitter_request.from_dict(create_remitter_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


