# CreateBeneficiaryRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**beneficiary_id** | **str** | Unique Beneficiary ID to identify the beneficiary. Alphanumeric characters and underscores are allowed. Maximum of 50 characters is allowed. | 
**account_holder_name** | **str** | Name of the beneficiary. Only alphabets are allowed. | 
**account_number** | **str** | Bank account number of the beneficiary. 9 - 25 alphanumeric characters are allowed. | 
**swift_code** | **str** | 8 to 11 character code in which first 6 characters are uppercase alphabets and the remaining are alphanumeric characters. | 
**iban** | **str** | IBAN of the beneficiary account. | [optional] 
**routing_number** | **str** | 9 digits routing number. | [optional] 
**bank_name** | **str** | Bank name of the beneficiary where the account exists. | 
**bank_address** | **str** | Bank address of the beneficiary where the account exists. | 
**bank_country** | **str** | Country where the beneficiary bank is located. | 
**sort_code** | **str** | Sort code of the country. Only numbers and hyphens are allowed. | [optional] 
**transit_code** | **str** | Transit code which consists of numbers between 5 to 10 in length. | [optional] 
**bsb_number** | **str** | BSB number is a 6 digit number code. | [optional] 
**address** | **str** | Address of the beneficiary. Only address alphanumeric characters, comma, dot, hyphens, and spaces are allowed. Maximum of 2000 charcaters is allowed. | 
**city** | **str** | City in which the beneficiary resides. Only alphabets are allowed. | 
**state** | **str** | State in which the beneficiary resides. Only alphabets are allowed. | 
**country** | **str** | Country in which the beneficiary resides. Only alphabets are allowed. | 
**postal_code** | **str** | Postal code of the beneficiary. Only alphanumeric characters are allowed. A maximum of 15 charcaters is allowed. | 

## Example

```python
from cashfree_lrs_client.models.create_beneficiary_request import CreateBeneficiaryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBeneficiaryRequest from a JSON string
create_beneficiary_request_instance = CreateBeneficiaryRequest.from_json(json)
# print the JSON string representation of the object
print CreateBeneficiaryRequest.to_json()

# convert the object into a dict
create_beneficiary_request_dict = create_beneficiary_request_instance.to_dict()
# create an instance of CreateBeneficiaryRequest from a dict
create_beneficiary_request_form_dict = create_beneficiary_request.from_dict(create_beneficiary_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


