# swagger_client.GeneralApi

All URIs are relative to *https://xbsbszzngd.execute-api.ap-south-1.amazonaws.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v1_clear_index_delete**](GeneralApi.md#v1_clear_index_delete) | **DELETE** /v1/clearIndex | /clearIndex
[**v1_delete_post**](GeneralApi.md#v1_delete_post) | **POST** /v1/delete | /delete
[**v1_index_post**](GeneralApi.md#v1_index_post) | **POST** /v1/index | /index
[**v1_search_get**](GeneralApi.md#v1_search_get) | **GET** /v1/search | /search (simple search)
[**v1_search_post**](GeneralApi.md#v1_search_post) | **POST** /v1/search | /search
[**v1_stats_get**](GeneralApi.md#v1_stats_get) | **GET** /v1/stats | /stats

# **v1_clear_index_delete**
> v1_clear_index_delete()

/clearIndex

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: api_key
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.GeneralApi(swagger_client.ApiClient(configuration))

try:
    # /clearIndex
    api_instance.v1_clear_index_delete()
except ApiException as e:
    print("Exception when calling GeneralApi->v1_clear_index_delete: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_delete_post**
> v1_delete_post(body=body, show_stats=show_stats, diag=diag)

/delete

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: api_key
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.GeneralApi(swagger_client.ApiClient(configuration))
body = NULL # object |  (optional)
show_stats = true # bool |  (optional)
diag = true # bool |  (optional)

try:
    # /delete
    api_instance.v1_delete_post(body=body, show_stats=show_stats, diag=diag)
except ApiException as e:
    print("Exception when calling GeneralApi->v1_delete_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional] 
 **show_stats** | **bool**|  | [optional] 
 **diag** | **bool**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_index_post**
> v1_index_post(body=body, diag=diag)

/index

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: api_key
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.GeneralApi(swagger_client.ApiClient(configuration))
body = NULL # object |  (optional)
diag = true # bool |  (optional)

try:
    # /index
    api_instance.v1_index_post(body=body, diag=diag)
except ApiException as e:
    print("Exception when calling GeneralApi->v1_index_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional] 
 **diag** | **bool**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_search_get**
> v1_search_get(q=q, key_list=key_list, page_size=page_size, page_index=page_index, diag=diag, show_stats=show_stats)

/search (simple search)

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: api_key
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.GeneralApi(swagger_client.ApiClient(configuration))
q = 56 # int |  (optional)
key_list = 'key_list_example' # str |  (optional)
page_size = 56 # int |  (optional)
page_index = 56 # int |  (optional)
diag = true # bool |  (optional)
show_stats = true # bool |  (optional)

try:
    # /search (simple search)
    api_instance.v1_search_get(q=q, key_list=key_list, page_size=page_size, page_index=page_index, diag=diag, show_stats=show_stats)
except ApiException as e:
    print("Exception when calling GeneralApi->v1_search_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **int**|  | [optional] 
 **key_list** | **str**|  | [optional] 
 **page_size** | **int**|  | [optional] 
 **page_index** | **int**|  | [optional] 
 **diag** | **bool**|  | [optional] 
 **show_stats** | **bool**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_search_post**
> v1_search_post(body=body, show_stats=show_stats, diag=diag, page_size=page_size, page_index=page_index)

/search

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: api_key
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.GeneralApi(swagger_client.ApiClient(configuration))
body = NULL # object |  (optional)
show_stats = true # bool |  (optional)
diag = true # bool |  (optional)
page_size = 56 # int |  (optional)
page_index = 56 # int |  (optional)

try:
    # /search
    api_instance.v1_search_post(body=body, show_stats=show_stats, diag=diag, page_size=page_size, page_index=page_index)
except ApiException as e:
    print("Exception when calling GeneralApi->v1_search_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional] 
 **show_stats** | **bool**|  | [optional] 
 **diag** | **bool**|  | [optional] 
 **page_size** | **int**|  | [optional] 
 **page_index** | **int**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v1_stats_get**
> v1_stats_get()

/stats

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: api_key
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.GeneralApi(swagger_client.ApiClient(configuration))

try:
    # /stats
    api_instance.v1_stats_get()
except ApiException as e:
    print("Exception when calling GeneralApi->v1_stats_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[api_key](../README.md#api_key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

