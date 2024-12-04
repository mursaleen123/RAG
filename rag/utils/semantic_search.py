# Standard Libraries
import json
import os
import sys

# Django settings
from django.conf import settings

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Azure Search Libraries
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

# Azure Libraries Credentials
from azure.core.credentials import AzureKeyCredential

# Models
#from MVPautomation.project.models import ProposalsModel

# Utils
from rag.utils import run_indexer


def create_semantic_search(self, data):
    '''
    Post request deploy a search in Azure AI and run a semantic search in Sharepoint Data source

    Entry parameters:
    data: Data body request from POST
    keywords: List of keywords to include in the query
    Optional: indexer_name (If its necessary to run manually the indexer to update the vector data)
    '''
    
    index_name = data.get('index_name')
    
    keywords = data.get('keywords')
    # Number of results to return
    top_results = data.get('n_results')

    # if 'proposal' in data:
    #     proposal_id = data.get('proposal')
    # else:
    #     # Mapping a static proposal to not break the workflow
    #     proposal_id = 1

    credential = AzureKeyCredential(settings.RAG_ADMIN_KEY)

    if 'indexer_name' in data:
        # Passing parameter ONLY if the indexer needs to run manually
        indexer_name = data.get('indexer_name')
        run_indexer(indexer_name, credential)

    # try:
    #     proposal = ProposalsModel.objects.get(id=proposal_id)
    # except AttributeError as e:
    #     raise Exception(f"Model not found: {e}")

    # Initialize the Search Client
    search_client = SearchClient(
        endpoint=settings.RAG_ENDPOINT, index_name=index_name, credential=credential
    )
    
    # document_names = []
    # output_directory = r"C:\Users\Wali Rehman\Downloads\sharepoint files 1"
    # output_file_path = os.path.join(output_directory, "document_names.txt")
    # os.makedirs(output_directory, exist_ok=True)
    

    try:
        # Run a semantic search query
        
        # search_results = search_client.search(
        #     search_text="*",  
        #     select="metadata_spo_item_name",   
        #     top=5000  
        # )
        
        # document_names = [result['metadata_spo_item_name'] for result in search_results]
        # with open(output_file_path, "w") as file:
        #     for name in document_names:
        #         file.write(name + "\n")  # Write each document name on a new line
        # print(f"Document names have been written to '{output_file_path}'")
    
        dynamic_query = ' OR '.join(keywords)

        query_prompt = f"""
            I have a dataset comprising multi-language documents (PDF, PPT, XLSX, DOCX). Perform a contextual search for: {dynamic_query}.
        """
        
        search_results = search_client.search(
            # search_text=keywords,
            # search_text=query_prompt.strip(),
            search_text=' OR '.join(keywords),
            query_type='semantic',
            search_mode='all', 
            semantic_configuration_name='prueba-sharepoint-semantic',  
            # semantic_configuration_name='research-folder-semantic',  
            query_answer='extractive',
            query_caption='extractive',
            top=100, 
            select='metadata_spo_item_name, content, metadata_spo_item_path',
            include_total_count=True,
            # vectors=[
            #     {
            #         "value": query_embedding,  # Query embedding
            #         "k": top_results,  # Number of results to return for vector search
            #         "fields": "DescriptionVector"  # Field in the index storing embeddings
            #     }
            # ],
            # search_fields=','.join(searchable_fields) if searchable_fields else None 
            #scoring_profile='keyword-match-scoring' 
        )
        print('Total Documents Matching Query:', search_results.get_count())
        print("-" * 50)

        return True,  search_results

    except Exception as data_error:
        print(f"Error at the Search query: {data_error}")
        return False, data_error
