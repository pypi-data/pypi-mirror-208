# swagger_client.TokensApi

All URIs are relative to *http://127.0.0.1:7000/credmgr/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**tokens_create_post**](TokensApi.md#tokens_create_post) | **POST** /tokens/create | Generate tokens for an user
[**tokens_refresh_post**](TokensApi.md#tokens_refresh_post) | **POST** /tokens/refresh | Refresh tokens for an user
[**tokens_revoke_post**](TokensApi.md#tokens_revoke_post) | **POST** /tokens/revoke | Revoke a refresh token for an user

# **tokens_create_post**
> Tokens tokens_create_post(project_id=project_id, scope=scope)

Generate tokens for an user

Request to generate tokens for an user 

### Example
```python
from __future__ import print_function
import time
from fabric_cm.credmgr.swagger_client import TokensApi
from fabric_cm.credmgr.swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = TokensApi()
project_id = 'project_id_example' # str | Project identified by universally unique identifier (optional)
scope = 'all' # str | Scope for which token is requested (optional) (default to all)

try:
    # Generate tokens for an user
    api_response = api_instance.tokens_create_post(project_id=project_id, scope=scope)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TokensApi->tokens_create_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**| Project identified by universally unique identifier | [optional] 
 **scope** | **str**| Scope for which token is requested | [optional] [default to all]

### Return type

[**Tokens**](Tokens.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **tokens_refresh_post**
> Tokens tokens_refresh_post(body, project_id=project_id, scope=scope)

Refresh tokens for an user

Request to refresh OAuth tokens for an user 

### Example
```python
from __future__ import print_function
import time
from fabric_cm.credmgr.swagger_client import TokensApi
from fabric_cm.credmgr.swagger_client.rest import ApiException
from fabric_cm.credmgr.swagger_client.models import Request
from pprint import pprint

# create an instance of the API class
api_instance = TokensApi()
body = Request() # Request | 
project_id = 'project_id_example' # str | Project identified by universally unique identifier (optional)
scope = 'all' # str | Scope for which token is requested (optional) (default to all)

try:
    # Refresh tokens for an user
    api_response = api_instance.tokens_refresh_post(body, project_id=project_id, scope=scope)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TokensApi->tokens_refresh_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Request**](Request.md)|  | 
 **project_id** | **str**| Project identified by universally unique identifier | [optional] 
 **scope** | **str**| Scope for which token is requested | [optional] [default to all]

### Return type

[**Tokens**](Tokens.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **tokens_revoke_post**
> Status200OkNoContent tokens_revoke_post(body)

Revoke a refresh token for an user

Request to revoke a refresh token for an user 

### Example
```python
from __future__ import print_function
import time
from fabric_cm.credmgr.swagger_client import TokensApi
from fabric_cm.credmgr.swagger_client.rest import ApiException
from fabric_cm.credmgr.swagger_client.models import Request
from pprint import pprint

# create an instance of the API class
api_instance = TokensApi()
body = Request() # Request | 

try:
    # Revoke a refresh token for an user
    api_response = api_instance.tokens_revoke_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TokensApi->tokens_revoke_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Request**](Request.md)|  | 

### Return type

[**Status200OkNoContent**](Status200OkNoContent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

