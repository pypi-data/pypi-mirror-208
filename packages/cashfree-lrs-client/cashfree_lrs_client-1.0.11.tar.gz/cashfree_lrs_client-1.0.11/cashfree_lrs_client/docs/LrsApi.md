# cashfree_lrs_client.LrsApi

All URIs are relative to *https://sandbox.cashfree.com/pg/lrs*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_documents_upload**](LrsApi.md#bulk_documents_upload) | **POST** /orders/documents/upload | Upload Documents in Bulk
[**create_beneficiary**](LrsApi.md#create_beneficiary) | **POST** /beneficiaries | Create Beneficiary
[**create_order**](LrsApi.md#create_order) | **POST** /orders | Create LRS Order
[**create_remitter**](LrsApi.md#create_remitter) | **POST** /remitters | Create Remitter
[**fetch_forex_rate**](LrsApi.md#fetch_forex_rate) | **POST** /fx-rate/details | Fetch FX Rate
[**process_order**](LrsApi.md#process_order) | **POST** /orders/{order_id}/process | Process Order
[**setup_webhooks**](LrsApi.md#setup_webhooks) | **POST** /webhooks | Setup Webhooks
[**upload_documents**](LrsApi.md#upload_documents) | **POST** /orders/{order_id}/documents/upload | Upload Documents


# **bulk_documents_upload**
> bulk_documents_upload(files)

Upload Documents in Bulk

Use this API to Upload documents before Order creation

### Example

* Api Key Authentication (X-Client-ID):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    files = [cashfree_lrs_client.bytearray()] # List[bytearray] | Upload multiple document at a time. Accepted file type - .pdf. Maximum file size - 20 MB

    try:
        # Upload Documents in Bulk
        api_instance.bulk_documents_upload(files)
    except Exception as e:
        print("Exception when calling LrsApi->bulk_documents_upload: %s\n" % e)
```

* Api Key Authentication (X-Client-Secret):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    files = [cashfree_lrs_client.bytearray()] # List[bytearray] | Upload multiple document at a time. Accepted file type - .pdf. Maximum file size - 20 MB

    try:
        # Upload Documents in Bulk
        api_instance.bulk_documents_upload(files)
    except Exception as e:
        print("Exception when calling LrsApi->bulk_documents_upload: %s\n" % e)
```

* Api Key Authentication (X-API-Version):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    files = [cashfree_lrs_client.bytearray()] # List[bytearray] | Upload multiple document at a time. Accepted file type - .pdf. Maximum file size - 20 MB

    try:
        # Upload Documents in Bulk
        api_instance.bulk_documents_upload(files)
    except Exception as e:
        print("Exception when calling LrsApi->bulk_documents_upload: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **files** | **List[bytearray]**| Upload multiple document at a time. Accepted file type - .pdf. Maximum file size - 20 MB | 

### Return type

void (empty response body)

### Authorization

[X-Client-ID](../README.md#X-Client-ID), [X-Client-Secret](../README.md#X-Client-Secret), [X-API-Version](../README.md#X-API-Version)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**413** | Example response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_beneficiary**
> SuccessMessage create_beneficiary(create_beneficiary_request=create_beneficiary_request)

Create Beneficiary

Use this API to create beneficiaries with Cashfree Payments from your backend.

### Example

* Api Key Authentication (X-Client-ID):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_beneficiary_request = cashfree_lrs_client.CreateBeneficiaryRequest() # CreateBeneficiaryRequest |  (optional)

    try:
        # Create Beneficiary
        api_response = api_instance.create_beneficiary(create_beneficiary_request=create_beneficiary_request)
        print("The response of LrsApi->create_beneficiary:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_beneficiary: %s\n" % e)
```

* Api Key Authentication (X-Client-Secret):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_beneficiary_request = cashfree_lrs_client.CreateBeneficiaryRequest() # CreateBeneficiaryRequest |  (optional)

    try:
        # Create Beneficiary
        api_response = api_instance.create_beneficiary(create_beneficiary_request=create_beneficiary_request)
        print("The response of LrsApi->create_beneficiary:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_beneficiary: %s\n" % e)
```

* Api Key Authentication (X-API-Version):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_beneficiary_request = cashfree_lrs_client.CreateBeneficiaryRequest() # CreateBeneficiaryRequest |  (optional)

    try:
        # Create Beneficiary
        api_response = api_instance.create_beneficiary(create_beneficiary_request=create_beneficiary_request)
        print("The response of LrsApi->create_beneficiary:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_beneficiary: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_beneficiary_request** | [**CreateBeneficiaryRequest**](CreateBeneficiaryRequest.md)|  | [optional] 

### Return type

[**SuccessMessage**](SuccessMessage.md)

### Authorization

[X-Client-ID](../README.md#X-Client-ID), [X-Client-Secret](../README.md#X-Client-Secret), [X-API-Version](../README.md#X-API-Version)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Example response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_order**
> CreateOrderResponse create_order(create_order_request=create_order_request)

Create LRS Order

Use this API to create orders with Cashfree Payments.

### Example

* Api Key Authentication (X-Client-ID):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_order_request = cashfree_lrs_client.CreateOrderRequest() # CreateOrderRequest |  (optional)

    try:
        # Create LRS Order
        api_response = api_instance.create_order(create_order_request=create_order_request)
        print("The response of LrsApi->create_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_order: %s\n" % e)
```

* Api Key Authentication (X-Client-Secret):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_order_request = cashfree_lrs_client.CreateOrderRequest() # CreateOrderRequest |  (optional)

    try:
        # Create LRS Order
        api_response = api_instance.create_order(create_order_request=create_order_request)
        print("The response of LrsApi->create_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_order: %s\n" % e)
```

* Api Key Authentication (X-API-Version):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_order_request = cashfree_lrs_client.CreateOrderRequest() # CreateOrderRequest |  (optional)

    try:
        # Create LRS Order
        api_response = api_instance.create_order(create_order_request=create_order_request)
        print("The response of LrsApi->create_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_order_request** | [**CreateOrderRequest**](CreateOrderRequest.md)|  | [optional] 

### Return type

[**CreateOrderResponse**](CreateOrderResponse.md)

### Authorization

[X-Client-ID](../README.md#X-Client-ID), [X-Client-Secret](../README.md#X-Client-Secret), [X-API-Version](../README.md#X-API-Version)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**400** | Example response |  -  |
**500** | Example response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_remitter**
> SuccessMessage create_remitter(create_remitter_request=create_remitter_request)

Create Remitter

Use this API to create remmiter account with Cashfree Payments for LRS transactions.

### Example

* Api Key Authentication (X-Client-ID):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_remitter_request = cashfree_lrs_client.CreateRemitterRequest() # CreateRemitterRequest |  (optional)

    try:
        # Create Remitter
        api_response = api_instance.create_remitter(create_remitter_request=create_remitter_request)
        print("The response of LrsApi->create_remitter:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_remitter: %s\n" % e)
```

* Api Key Authentication (X-Client-Secret):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_remitter_request = cashfree_lrs_client.CreateRemitterRequest() # CreateRemitterRequest |  (optional)

    try:
        # Create Remitter
        api_response = api_instance.create_remitter(create_remitter_request=create_remitter_request)
        print("The response of LrsApi->create_remitter:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_remitter: %s\n" % e)
```

* Api Key Authentication (X-API-Version):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    create_remitter_request = cashfree_lrs_client.CreateRemitterRequest() # CreateRemitterRequest |  (optional)

    try:
        # Create Remitter
        api_response = api_instance.create_remitter(create_remitter_request=create_remitter_request)
        print("The response of LrsApi->create_remitter:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->create_remitter: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_remitter_request** | [**CreateRemitterRequest**](CreateRemitterRequest.md)|  | [optional] 

### Return type

[**SuccessMessage**](SuccessMessage.md)

### Authorization

[X-Client-ID](../README.md#X-Client-ID), [X-Client-Secret](../README.md#X-Client-Secret), [X-API-Version](../README.md#X-API-Version)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Example response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **fetch_forex_rate**
> fetch_forex_rate(fetch_forex_rate_request=fetch_forex_rate_request)

Fetch FX Rate

Use this API to get the foreign exchange rate.

### Example

* Api Key Authentication (X-Client-ID):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    fetch_forex_rate_request = cashfree_lrs_client.FetchForexRateRequest() # FetchForexRateRequest |  (optional)

    try:
        # Fetch FX Rate
        api_instance.fetch_forex_rate(fetch_forex_rate_request=fetch_forex_rate_request)
    except Exception as e:
        print("Exception when calling LrsApi->fetch_forex_rate: %s\n" % e)
```

* Api Key Authentication (X-Client-Secret):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    fetch_forex_rate_request = cashfree_lrs_client.FetchForexRateRequest() # FetchForexRateRequest |  (optional)

    try:
        # Fetch FX Rate
        api_instance.fetch_forex_rate(fetch_forex_rate_request=fetch_forex_rate_request)
    except Exception as e:
        print("Exception when calling LrsApi->fetch_forex_rate: %s\n" % e)
```

* Api Key Authentication (X-API-Version):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    fetch_forex_rate_request = cashfree_lrs_client.FetchForexRateRequest() # FetchForexRateRequest |  (optional)

    try:
        # Fetch FX Rate
        api_instance.fetch_forex_rate(fetch_forex_rate_request=fetch_forex_rate_request)
    except Exception as e:
        print("Exception when calling LrsApi->fetch_forex_rate: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **fetch_forex_rate_request** | [**FetchForexRateRequest**](FetchForexRateRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[X-Client-ID](../README.md#X-Client-ID), [X-Client-Secret](../README.md#X-Client-Secret), [X-API-Version](../README.md#X-API-Version)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **process_order**
> process_order(order_id)

Process Order

Use this API to process an order.

### Example

* Api Key Authentication (X-Client-ID):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    order_id = 'order_id_example' # str | The subject Order ID

    try:
        # Process Order
        api_instance.process_order(order_id)
    except Exception as e:
        print("Exception when calling LrsApi->process_order: %s\n" % e)
```

* Api Key Authentication (X-Client-Secret):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    order_id = 'order_id_example' # str | The subject Order ID

    try:
        # Process Order
        api_instance.process_order(order_id)
    except Exception as e:
        print("Exception when calling LrsApi->process_order: %s\n" % e)
```

* Api Key Authentication (X-API-Version):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    order_id = 'order_id_example' # str | The subject Order ID

    try:
        # Process Order
        api_instance.process_order(order_id)
    except Exception as e:
        print("Exception when calling LrsApi->process_order: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**| The subject Order ID | 

### Return type

void (empty response body)

### Authorization

[X-Client-ID](../README.md#X-Client-ID), [X-Client-Secret](../README.md#X-Client-Secret), [X-API-Version](../README.md#X-API-Version)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **setup_webhooks**
> SuccessMessage setup_webhooks(setup_webhooks_request=setup_webhooks_request)

Setup Webhooks

Use this API to configure webhook URLs to receive updates about payments, refunds, and orders.

### Example

* Api Key Authentication (X-Client-ID):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    setup_webhooks_request = {"payment_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592","refund_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592","order_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592"} # SetupWebhooksRequest |  (optional)

    try:
        # Setup Webhooks
        api_response = api_instance.setup_webhooks(setup_webhooks_request=setup_webhooks_request)
        print("The response of LrsApi->setup_webhooks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->setup_webhooks: %s\n" % e)
```

* Api Key Authentication (X-Client-Secret):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    setup_webhooks_request = {"payment_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592","refund_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592","order_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592"} # SetupWebhooksRequest |  (optional)

    try:
        # Setup Webhooks
        api_response = api_instance.setup_webhooks(setup_webhooks_request=setup_webhooks_request)
        print("The response of LrsApi->setup_webhooks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->setup_webhooks: %s\n" % e)
```

* Api Key Authentication (X-API-Version):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    setup_webhooks_request = {"payment_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592","refund_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592","order_url":"https://webhook.site/da93ae47-4bdf-4b2b-9144-56e57a345592"} # SetupWebhooksRequest |  (optional)

    try:
        # Setup Webhooks
        api_response = api_instance.setup_webhooks(setup_webhooks_request=setup_webhooks_request)
        print("The response of LrsApi->setup_webhooks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->setup_webhooks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **setup_webhooks_request** | [**SetupWebhooksRequest**](SetupWebhooksRequest.md)|  | [optional] 

### Return type

[**SuccessMessage**](SuccessMessage.md)

### Authorization

[X-Client-ID](../README.md#X-Client-ID), [X-Client-Secret](../README.md#X-Client-Secret), [X-API-Version](../README.md#X-API-Version)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_documents**
> object upload_documents(order_id, files)

Upload Documents

Use this API to Upload documents on your Order ID.

### Example

* Api Key Authentication (X-Client-ID):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    order_id = 'order_id_example' # str | The subject Order ID
    files = [cashfree_lrs_client.bytearray()] # List[bytearray] | Upload multiple document at a time. Accepted file type - .pdf. Maximum file size - 20 MB

    try:
        # Upload Documents
        api_response = api_instance.upload_documents(order_id, files)
        print("The response of LrsApi->upload_documents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->upload_documents: %s\n" % e)
```

* Api Key Authentication (X-Client-Secret):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    order_id = 'order_id_example' # str | The subject Order ID
    files = [cashfree_lrs_client.bytearray()] # List[bytearray] | Upload multiple document at a time. Accepted file type - .pdf. Maximum file size - 20 MB

    try:
        # Upload Documents
        api_response = api_instance.upload_documents(order_id, files)
        print("The response of LrsApi->upload_documents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->upload_documents: %s\n" % e)
```

* Api Key Authentication (X-API-Version):
```python
from __future__ import print_function
import time
import os
import cashfree_lrs_client
from cashfree_lrs_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to https://sandbox.cashfree.com/pg/lrs
# See configuration.py for a list of all supported configuration parameters.
configuration = cashfree_lrs_client.Configuration(
    host = "https://sandbox.cashfree.com/pg/lrs"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: X-Client-ID
configuration.api_key['X-Client-ID'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-ID'] = 'Bearer'

# Configure API key authorization: X-Client-Secret
configuration.api_key['X-Client-Secret'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Client-Secret'] = 'Bearer'

# Configure API key authorization: X-API-Version
configuration.api_key['X-API-Version'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-Version'] = 'Bearer'

# Enter a context with an instance of the API client
with cashfree_lrs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = cashfree_lrs_client.LrsApi(api_client)
    order_id = 'order_id_example' # str | The subject Order ID
    files = [cashfree_lrs_client.bytearray()] # List[bytearray] | Upload multiple document at a time. Accepted file type - .pdf. Maximum file size - 20 MB

    try:
        # Upload Documents
        api_response = api_instance.upload_documents(order_id, files)
        print("The response of LrsApi->upload_documents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LrsApi->upload_documents: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**| The subject Order ID | 
 **files** | **List[bytearray]**| Upload multiple document at a time. Accepted file type - .pdf. Maximum file size - 20 MB | 

### Return type

**object**

### Authorization

[X-Client-ID](../README.md#X-Client-ID), [X-Client-Secret](../README.md#X-Client-Secret), [X-API-Version](../README.md#X-API-Version)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Example response |  -  |
**404** | Example response |  -  |
**413** | Example response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

