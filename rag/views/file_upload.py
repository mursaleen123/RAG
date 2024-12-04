# Standard Libraries
import json
import os

# Django settings
from django.conf import settings

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

# Django Storage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Azure Libraries Credentials
from azure.core.credentials import AzureKeyCredential

# Utils
from rag.utils import index_chunks_to_search


class FileUploadAPIView(APIView):
    '''
        API View for handling file uploads

        - Accepts a file via POST request and saves it to the default storage.
        - Returns the file path or an error message.
    '''

    def post(self, request, *args, **kwargs):
        '''
        Handle file upload and return the saved file name or error.

        Entry parameters:
        - file: File to upload.

        Return:
        - File name if successful, error message otherwise.
        '''

        # Step 1: Get file from the request
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Save the file to the default storage location
        file_name = default_storage.save(file.name, ContentFile(file.read()))
        file_path = os.path.join(settings.MEDIA_ROOT , file_name)
        print(f"File path: {file_path}")
        
        # Step 3: Create file metadata (can be extended as needed)
        file_metadata = {
            "id": file_name,  
            "webUrl": os.path.join(settings.MEDIA_ROOT , file_name),   
            "lastModifiedDateTime": "2024-12-01T12:00:00Z"  # Set a last modified date (could be dynamic)
        }

        # Step 4: Credentials and index details for Azure Search
        credential = AzureKeyCredential (settings.RAG_ADMIN_KEY)
        index_name = "prueba-sharepoint-index"  

        # Step 5: Index the file content in chunks
        try:
            index_chunks_to_search(file_metadata, credential, index_name)
            return Response({"message": f"File {file_name} uploaded and indexed successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error indexing the file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)