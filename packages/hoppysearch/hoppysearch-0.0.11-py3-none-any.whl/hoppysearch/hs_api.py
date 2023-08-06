import io
from .api.general_api import GeneralApi
from .configuration import Configuration
from .dictToClass import DictToClass
import json

def unknownField(known_field, obj):
    for key in obj:
        if key not in known_field:
            print(f"Warning: Received unknown key {key}.")

def convetResponseToJSON(response):
    if (response.status == 200):
        json_data = json.loads(response.data.decode('utf-8'))
        if isinstance(json_data, dict):
            return DictToClass(**json_data)
        else:
            return json_data
    else:
        return response

class HoppySearch(GeneralApi):
    def __init__(self, index_id=None, api_key=None):
        if index_id is None or api_key is None:
            raise TypeError("Both indexId and apiKey are mandatory")
        
        config = Configuration(index_id)
        config.api_key['Authorization'] = 'hs_f3vrd6tqwzcc01oh'

        super().__init__()

        self.clear_index = self.clear_index
        self.delete = self.delete
        self.index = self.index
        self.search = self.search
        self.lucene_search = self.lucene_search
        self.stats = self.stats

    def index(self, documents, optionals={}):
        if not documents:
            raise ValueError('Please pass your data which you want to index.')
        if not (isinstance(documents, list) or isinstance(documents, str) or isinstance(documents, io.IOBase)):
            raise TypeError("Please ensure that the first argument is of the correct datatype. It can either be a list (for direct data upload), a string (for upload through a filepath), or an io.IOBase object (for upload through a file object).")
        
        if isinstance(documents, str):
            with open(documents) as file:
                json_data = json.load(file)
            documents = json_data
        elif isinstance(documents, io.IOBase):
            documents = json.loads(documents.read())

        knownField = ['diag', 'configType']
        if optionals:
            unknownField(knownField, optionals)

        opts = {
            'body': {
                'documents': documents,
                'config': {
                    'type': optionals.get('configType', 'append')
                }
            },
            'diag': optionals.get('diag', False)
        }
        
        response = super().v1_index_post(**opts)
        return convetResponseToJSON(response)
    
    def search(self, query, optionals={}):
        if not query:
            raise ValueError('Please pass your query as first argument.')
        if not isinstance(query, str):
            raise ValueError('Your first argument "query" should be of type "str".')
        
        knownField = ['searchableKeyList', 'pageSize', 'pageIndex', 'diag', 'showStats']
        unknownField(knownField, optionals)

        opts = {
            'q': query,
            'key_list': optionals.get('searchableKeyList', ''),
            'diag': optionals.get('diag', False),
            'show_stats': optionals.get('showStats', False),
            'page_size': optionals.get('pageSize', 50),
            'page_index': optionals.get('pageIndex', 0)
        }
        
        response = super().v1_search_get(**opts)
        return convetResponseToJSON(response)

    def lucene_search(self, lucene_query, optionals={}):
        if not lucene_query:
            raise ValueError("Please pass your luceneQuery as first argument.")
        if not isinstance(lucene_query, str):
            raise ValueError('Your first argument "lucene_query" should be of type "str".')

        knownField = ['pageSize', 'pageIndex', 'diag', 'showStats', 'defaultKeyNameToBeSearch', 'analyzerClass']
        unknownField(knownField, optionals)

        opts = {
            'body': {
                'luceneQuery': lucene_query
            },
            'diag': optionals['diag'] if optionals and 'diag' in optionals else False,
            'show_stats': optionals['showStats'] if optionals and 'showStats' in optionals else False,
            'page_size': optionals['pageSize'] if optionals and 'pageSize' in optionals else 50,
            'page_index': optionals['pageIndex'] if optionals and 'pageIndex' in optionals else 0
        }

        if optionals and 'defaultKeyNameToBeSearch' in optionals:
            opts['body']['defaultKeyNameToBeSearch'] = optionals['defaultKeyNameToBeSearch']
        if optionals and 'analyzerClass' in optionals:
            opts['body']['analyzerClass'] = optionals['analyzerClass']

        response =  self.v1_search_post(**opts)
        return convetResponseToJSON(response)

    def delete(self, hs_guid, optionals={}):
        if not hs_guid:
            raise ValueError('Please pass your hs_guid as first argument.')
        if not isinstance(hs_guid, str):
            raise ValueError('Your first argument "hs_guid" should be of type "str".')
        knownField = ['diag', 'showStats']
        unknownField(knownField, optionals)
        opts = {
            'body': {
                'hs_guid': hs_guid
            },
            'diag': optionals.get('diag', False),
            'show_stats': optionals.get('showStats', False)
        }
        response = super().v1_delete_post(**opts)
        return convetResponseToJSON(response)
    
    def stats(self):
        response = self.v1_stats_get()
        return convetResponseToJSON(response)
    
    def clear_index(self):
        response = super().v1_clear_index_delete()
        return convetResponseToJSON(response)
