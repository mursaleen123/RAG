# Standard Libraries
import json
import requests

# Django
from django.conf import settings

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Utils
from sharepoint.utils.copy_files import copy_file_to_destination

class CopyFilesSharepointView(APIView):
    ''' Get specific URL file stored in Sharepoint and copy into another path folder  '''

    def post(self, request, *args, **kwargs):

        # Get data from the POST body request
        data = json.loads(request.body)
        source_file_url = data.get('source_path')
        destination_folder_url = data.get('destination_path')

        status_code, message = copy_file_to_destination(source_file_url, destination_folder_url)

        if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return Response({'error': message}, status=status_code)

        return Response(message, status=status_code)
