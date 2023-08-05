# swagger_client.DefaultApi

All URIs are relative to *http://127.0.0.1:7000/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**certs_get**](DefaultApi.md#certs_get) | **GET** /certs | Return Public Keys to verify signature of the tokens

# **certs_get**
> Jwks certs_get()

Return Public Keys to verify signature of the tokens

Json Web Keys

### Example
```python
from __future__ import print_function
import time
from fabric_cm.credmgr.swagger_client import DefaultApi
from fabric_cm.credmgr.swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = DefaultApi()

try:
    # Return Public Keys to verify signature of the tokens
    api_response = api_instance.certs_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->certs_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Jwks**](Jwks.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

