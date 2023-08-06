# hoppysearch

hoppysearch - Python client for hoppysearch

## Requirements.

Python 2.7 and 3.4+

## Installation & Usage
### pip install

Install it via:

```sh
pip install hoppysearch
```

Then import the package:
```python
from hoppysearch import HoppySearch, ApiException
```
## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

#### Initial configuration:
```python
from hoppysearch import HoppySearch, ApiException
index_id = YOUR_INDEX_ID
api_key = YOUR_API_KEY
hoppysearch = HoppySearch(index_id, api_key )
```

### index
Please add the below code after Initial configuration to index your data.
```python
documents = [
    {
        "Id": 101872,
        "ProductId": "B000DZH1D6",
        "UserId": "A1HKBX2L0DV258",
        "ProfileName": "Dena Leasure",
        "HelpfulnessNumerator": 0,
        "HelpfulnessDenominator": 0,
        "Score": 5,
        "Time": 1259625600,
        "Summary": "Gluten free cookies",
        "Text": "These are the best cookies I have found that are gluten free.  I love them!"
    }
]

optionals = {
    "configType": "create",
    "diag": "true"
}

try:
    response = hoppysearch.index(documents, optionals)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```


The second argument of hoppysearch.index is not mandatory. You can skip it fully or you can skip any key value according to your requirement.


```python
# skip second argument
documents = [
    {
        "Id": 101872,
        "ProductId": "B000DZH1D6",
        "UserId": "A1HKBX2L0DV258",
        "ProfileName": "Dena Leasure",
        "HelpfulnessNumerator": 0,
        "HelpfulnessDenominator": 0,
        "Score": 5,
        "Time": 1259625600,
        "Summary": "Gluten free cookies",
        "Text": "These are the best cookies I have found that are gluten free.  I love them!"
    }
]

try:
    response = hoppysearch.index(documents)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

```python
# skip some key of second argument
documents = [
    {
        "Id": 101872,
        "ProductId": "B000DZH1D6",
        "UserId": "A1HKBX2L0DV258",
        "ProfileName": "Dena Leasure",
        "HelpfulnessNumerator": 0,
        "HelpfulnessDenominator": 0,
        "Score": 5,
        "Time": 1259625600,
        "Summary": "Gluten free cookies",
        "Text": "These are the best cookies I have found that are gluten free.  I love them!"
    }
]

optionals = {
    "diag": "true"
}

try:
    response = hoppysearch.index(documents)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

You can pass file object or file path to upload data to index.
```python
# filepath
documents = "C:/Users/Pragyan/Desktop/books.json"

try:
    response = hoppysearch.index(documents)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

```python
# fileobj
documents = open("C:/Users/Pragyan/Desktop/books.json", "r")

try:
    response = hoppysearch.index(documents)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

### search
First add the configuration as mentioned above and then add below code to search.
```python
query = "cookies"
optionals = {
    "searchableKeyList": "Summary, Text",
    "diag": "true",
    "showStats": "true",
    "pageSize": 10,
    "pageIndex": 0
}

try:
    response = hoppysearch.search(query, optionals)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

The second argument of hoppysearch.search is not mandatory. You can skip it fully or you can skip any key value according to your requirement.

```python
# skip second argument
query = "cookies"
try:
    response = hoppysearch.search(query)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```
```python
# skip some key of second argument
query = "cookies"
optionals = {
    "searchableKeyList": "Summary, Text",
    "pageSize": 10,
    "pageIndex": 0
}

try:
    response = hoppysearch.search(query)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

### luceneSearch
First add the configuration as mentioned above and then add below code to perform search in advaced way.
```python
luceneQuery = "Text: cookies"
optionals = {
    "defaultKeyNameToBeSearch": "Summary",
    "analyzerClass": "org.apache.lucene.analysis.standard.StandardAnalyzer",
    "diag": True,
    "showStats": True,
    "pageSize": 10,
    "pageIndex": 0
}

try:
    response = hoppysearch.lucene_search(luceneQuery, optionals)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

The second argument of hoppysearch.lucene_search is not mandatory. You can skip it fully or you can skip any key value according to your requirement.
```python
# skip second argument
luceneQuery = "Text: cookies"
try:
    response = hoppysearch.lucene_search(luceneQuery)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```
```python
# skip some key of second argument
luceneQuery = "Text: cookies"
optionals = {
    "defaultKeyNameToBeSearch": "Summary",
    "pageSize": 10,
    "pageIndex": 0
}

try:
    response = hoppysearch.lucene_search(luceneQuery, optionals)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

### delete
First add the configuration as mentioned above and then add below code to delete specific data from index.

```python
hs_guid = "15b522d8-1545-4dc9-9160-0b512f7d6997"
optionals = {
    "diag": True,
    "showStats": True
}

try:
    response = hoppysearch.delete(hs_guid, optionals)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```


The second argument of hoppysearch.delete is not mandatory. You can skip it fully or you can skip any key value according to your requirement.

```python
# skip second argument
hs_guid = "15b522d8-1545-4dc9-9160-0b512f7d6997"
try:
    response = hoppysearch.delete(hs_guid)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

```python
# skip some key of second argument
hs_guid = "15b522d8-1545-4dc9-9160-0b512f7d6997"
optionals = {
    "diag": True
}

try:
    response = hoppysearch.delete(hs_guid, optionals)
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

### stats
First add the configuration as mentioned above and then add below code to get stats.

```python
try:
    response = hoppysearch.stats()
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```

### clearIndex
First add the configuration as mentioned above and then add below code to clear all data from your index.

```python
try:
    response = hoppysearch.clear_index()
    print(response)
except ApiException as e:
    print("Exception: %s\n" % e)
```
