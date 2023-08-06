from src.hoppysearch.hs_api import HoppySearch
from src.hoppysearch.rest import ApiException

index_id ="lucene-serverless"
api_key ="hs_f3vrd6tqwzcc01oh"
hoppysearch = HoppySearch(index_id, api_key )


# # index
# # ===============================================================================================
# documents = [
#     {
#         "Id": 101872,
#         "ProductId": "B000DZH1D6",
#         "UserId": "A1HKBX2L0DV258",
#         "ProfileName": "Dena Leasure",
#         "HelpfulnessNumerator": 0,
#         "HelpfulnessDenominator": 0,
#         "Score": 5,
#         "Time": 1259625600,
#         "Summary": "Gluten free cookies",
#         "Text": "These are the best cookies I have found that are gluten free.  I love them!"
#     }
# ]

# # filepath
# documents = "C:/Users/Pragyan/Desktop/books.json"

# # fileobj
# documents = open("C:/Users/Pragyan/Desktop/books.json", "r")

# optionals = {
#     "configType": "create",
#     "diag": "true"
# }

# try:
#     response = hoppysearch.index(documents, optionals)
#     print(response.indexResponse)
# except ApiException as e:
#     print("Exception: %s\n" % e)

# # without optionals
# try:
#     response = hoppysearch.index(documents)
#     print(response)
# except ApiException as e:
#     print("Exception: %s\n" % e)




# # search
# # ===============================================================================================
# query = "cookies"
# optionals = {
#     "searchableKeyList": "Summary, Text",
#     "diag": "true",
#     "showStats": "true",
#     "pageSize": 10,
#     "pageIndex": 0
# }

# try:
#     response = hoppysearch.search(query, optionals)
#     print(response)
# except ApiException as e:
#     print("Exception: %s\n" % e)

# # without optionals
# try:
#     response = hoppysearch.search(query)
#     print(response)
# except ApiException as e:
#     print("Exception: %s\n" % e)




# # LuceneSearch
# # ===============================================================================================
# luceneQuery = "Text: cookies"
# optionals = {
#     "defaultKeyNameToBeSearch": "Summary",
#     "analyzerClass": "org.apache.lucene.analysis.standard.StandardAnalyzer",
#     "diag": True,
#     "showStats": True,
#     "pageSize": 10,
#     "pageIndex": 0
# }

# try:
#     response = hoppysearch.lucene_search(luceneQuery, optionals)
#     print(response)
# except ApiException as e:
#     print("Exception: %s\n" % e)

# # without optionals
# try:
#     response = hoppysearch.lucene_search(luceneQuery)
#     print(response)
# except ApiException as e:
#     print("Exception: %s\n" % e)





# # delete
# # ====================================================================================
# hs_guid = "15b522d8-1545-4dc9-9160-0b512f7d6997"
# optionals = {
#     "diag": True,
#     "showStats": True
# }

# try:
#     response = hoppysearch.delete(hs_guid, optionals)
#     print(response)
# except ApiException as e:
#     print("Exception: %s\n" % e)

# # without optionals
# try:
#     response = hoppysearch.delete(hs_guid)
#     print(response)
# except ApiException as e:
#     print("Exception: %s\n" % e)



# stats
# ====================================================================================
try:
    response = hoppysearch.stats()
    print(response.totalDocs)
except ApiException as e:
    print("Exception: %s\n" % e)




# # clear_index
# # ====================================================================================
# try:
#     response = hoppysearch.clear_index()
#     print(response)
# except ApiException as e:
#     print("Exception: %s\n" % e)