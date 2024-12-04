# Standard Libraries
import os
import requests
import json

# Django
from django.conf import settings

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Memory
from io import BytesIO

# Permissions
from rest_framework.permissions import AllowAny

# Office Library
from pptx import Presentation

# Utils
from sharepoint.utils import (
    get_sp_file, upload_ppt_file, delete_slide_by_tittle
)


class DeleteSlidesSharepointAPIView(APIView):

    ''' Class view for Delete slides in PPTX files stored in Sharepoint '''

    permission_classes = [AllowAny]

    def post(self, request):

        # Get data from the POST body request
        data = json.loads(request.body)
        file_path = data.get('file')
        tittle_keys = data.get('keywords')

        presentation_url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFileByServerRelativeUrl('{file_path}')/$value"

        ppt_file = get_sp_file(presentation_url)

        try:
            presentation = Presentation(ppt_file)
        except Exception as e:
            raise Exception(f"Failed to open presentation: {e}")

        delete_slide_by_tittle(presentation, tittle_keys)

        # Save the modified presentation to an in-memory buffer
        modified_file = BytesIO()
        presentation.save(modified_file)
        modified_file.seek(0)

        upload_ppt_file(presentation_url, modified_file)

        return Response({'message': 'slides remove succesfully'}, status=status.HTTP_200_OK)

