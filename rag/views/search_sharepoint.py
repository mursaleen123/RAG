# Standard Libraries
import json

# Django settings
from django.conf import settings

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Azure Search Libraries
from azure.search.documents import SearchClient

# Azure Libraries Credentials
from azure.core.credentials import AzureKeyCredential

# Utils
from rag.utils import run_indexer, create_prompt_request, create_semantic_search


class IndexationAPIView(APIView):
    '''
        API View for RAG processes

        - Semantic Search
        - Azure OpenAI
        - Azure AI Search
    '''

    def post(self, request, *args, **kwargs):
        '''
        Post request deploy a search in Azure AI and call OpenAI to pass the results of the search
        and make an advanced search.

        Entry parameters: index name
        Optional: indexer_name (If its necessary to run manually the indexer to update the vector data)
        '''

        data = json.loads(request.body)
        
        action = data.get('action')
        
        # Process to only list files in semantic search without OpenAI
        if action == 'list_files':
            return self.search_files(data)

        state,  results = create_semantic_search(self, data)
        serializable_results = [
            {
                'metadata_spo_item_name': result.get('metadata_spo_item_name', ''),
                'content': result.get('content', ''),
                'metadata_spo_item_path': result.get('metadata_spo_item_path', '')
            }
            for result in results
        ]
        if state is False:
            raise Exception(f"No results found: {results}")

        # response_chat, state = create_prompt_request(data, action, results)

        if state is False:
            return Response(serializable_results, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializable_results, status=status.HTTP_200_OK)


    def search_files(self, data):
        '''
        Function to perform semantic search and return a list of mutiple related files

        - data:

        - Return: The list of files found in the semantic search
        '''

        index_name = data.get('index_name')
        keywords = data.get('keywords')
        top_results = data.get('n_results')

        credential = AzureKeyCredential(settings.RAG_ADMIN_KEY)

        # Initialize the Search Client
        search_client = SearchClient(
            endpoint=settings.RAG_ENDPOINT, index_name=index_name, credential=credential
        )

        try:
            # Run a semantic search query
            results = search_client.search(
                query_type='semantic',
                search_text=keywords,
                semantic_configuration_name='research-folder-semantic', # Semantic Configuration Name from Azure AI Search
                query_answer='extractive',
                query_caption='extractive',
                top=top_results, # Number of results to retrieve from the search
                select='metadata_spo_item_name, metadata_spo_item_path',
                include_total_count=True
            )

        except Exception as data_error:
            return Response(data_error, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Remove a parameter that contains a objec Non serializable
        key_to_remove = '@search.captions'
        data_files = [{key: value for key, value in result.items() if key != key_to_remove} for result in results]

        # print('Total Documents Matching Query:', results.get_count())

        return Response(data_files, status=status.HTTP_200_OK)