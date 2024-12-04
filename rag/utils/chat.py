# Standard Libraries
import os

# Azure OpenAI
from openai import AzureOpenAI

# NOT USED FOR RAG
# def call_chat_with_rag(prompt):
#     """
#     Calls the OpenAI API to get a response based on the prompt.
#     """

#     # Initialize Azure OpenAI client with key-based authentication
#     client = AzureOpenAI(
#         azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
#         api_key = os.getenv("AZURE_OPENAI_API_KEY"),
#         api_version = "2024-05-01-preview",
#     )

#     completion = client.chat.completions.create(
#         model=os.getenv("AZURE_DEPLOYMENT_MODEL"),
#         messages= prompt,
#         temperature=0.5,
#         top_p=0.95,
#         frequency_penalty=0,
#         presence_penalty=0,
#         stop=None,
#         stream=False
#     ,
#         extra_body={
#         "data_sources": [{
#             "type": "azure_search",
#             "parameters": {
#                 "endpoint": f"{os.getenv('RAG_ENDPOINT')}",
#                 "index_name": f"prueba-sharepoint-index",
#                 "semantic_configuration": "prueba-sharepoint-semantic",
#                 "query_type": "semantic",
#                 "fields_mapping": {
#                 "content_fields_separator": "\n",
#                 "content_fields": [
#                     "content"
#                 ],
#                 "filepath_field": "id",
#                 "title_field": "metadata_spo_item_name",
#                 "url_field": "metadata_spo_item_path",
#                 "vector_fields": []
#                 },
#                 "in_scope": True,
#                 "role_information": "I am an AI assistant designed to help users find information efficiently ",
#                 "filter": None,
#                 "strictness": 3,
#                 "top_n_documents": 5,
#                 "authentication": {
#                 "type": "api_key",
#                 "key": f"{os.getenv('RAG_ADMIN_KEY')}"
#                 }
#             }
#             }]
#         })

#     return completion.choices[0].message.content.strip()
