# ResourcesApi

All URIs are relative to *http://127.0.0.1:8700/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**portalresources_get**](ResourcesApi.md#portalresources_get) | **GET** /portalresources | Retrieve a listing and description of available resources for portal
[**resources_get**](ResourcesApi.md#resources_get) | **GET** /resources | Retrieve a listing and description of available resources. By default, a cached available resource information is returned. User can force to request the current available resources.

# **portalresources_get**
> Resources portalresources_get(graph_format)

Retrieve a listing and description of available resources for portal

Retrieve a listing and description of available resources for portal

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import ResourcesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = ResourcesApi()
graph_format = 'GRAPHML' # str | graph format (default to GRAPHML)

try:
    # Retrieve a listing and description of available resources for portal
    api_response = api_instance.portalresources_get(graph_format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ResourcesApi->portalresources_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **graph_format** | **str**| graph format | [default to GRAPHML]

### Return type

[**Resources**](Resources.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resources_get**
> Resources resources_get(level, force_refresh)

Retrieve a listing and description of available resources. By default, a cached available resource information is returned. User can force to request the current available resources.

Retrieve a listing and description of available resources. By default, a cached available resource information is returned. User can force to request the current available resources.

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import ResourcesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = ResourcesApi(ApiClient(configuration))
level = 1 # int | Level of details (default to 1)
force_refresh = False # bool | Force to retrieve current available resource information. (default to false)

try:
    # Retrieve a listing and description of available resources. By default, a cached available resource information is returned. User can force to request the current available resources.
    api_response = api_instance.resources_get(level, force_refresh)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ResourcesApi->resources_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **level** | **int**| Level of details | [default to 1]
 **force_refresh** | **bool**| Force to retrieve current available resource information. | [default to false]

### Return type

[**Resources**](Resources.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

