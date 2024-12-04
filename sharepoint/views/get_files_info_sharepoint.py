# Standard Libraries
import json
import requests

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from sharepoint.utils.files import get_unique_id

# Utils


class SharePointFileInfoView(APIView):

    def get(self, request, *args, **kwargs):
        folder_path = request.GET.get('folder_path')

        if folder_path is None:
            return Response({'message': 'Folder path is required'}, status=status.HTTP_400_BAD_REQUEST)

        response_id = get_unique_id(folder_path=folder_path)

        if isinstance(response_id, Response):
            return response_id
        else:
            return Response({'message': 'Success', 'response_id': response_id}, status=status.HTTP_200_OK)

