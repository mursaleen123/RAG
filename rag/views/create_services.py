# Standard Libraries
import json

# Django settings
from django.conf import settings

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Azure Libraries Credentials
from azure.core.credentials import AzureKeyCredential


# Utils
from sharepoint.utils import get_files_from_library, get_file_size

from rag.utils import (
    create_connection_data_source, run_indexer,
    create_search_index, setup_indexer, get_datasource_connection,
    # index_chunks_to_search
)


class CreateRAGServicesAPIView(APIView):
    '''
        API View for RAG processes

        - Semantic Search
        - Azure OpenAI
        - Azure AI Search
    '''

    def post(self, request, *args, **kwargs):
        ''' View to create RAG services '''

        data = json.loads(request.body)

        index_name = data.get('index_name')

        credential = AzureKeyCredential(settings.RAG_ADMIN_KEY)

        if 'data_source' in data:
            data_source = data.get('data_source')

            create_connection_data_source(data_source, credential)

        create_search_index(index_name, credential)

        if 'indexer_name' in data:
            indexer_name = data.get('indexer_name')

            setup_indexer(indexer_name, data_source, index_name, credential)

        return Response(f"Services created succesfully", status=status.HTTP_200_OK)
