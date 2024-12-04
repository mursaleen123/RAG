# Standard Libraries
import json
import requests

# Python retrying Libraries
from tenacity import retry, wait_fixed, stop_after_attempt

# Django
from django.conf import settings
from django.http import HttpResponse

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Utils
from sharepoint.utils.files import get_unique_id
#from MVPautomation.utils.utils_token import refresh_token, is_token_expired, get_actual_token


class SharePointFileView(APIView):
    '''
    Get specific file by the path provided
    '''

    def post(self, request, *args, **kwargs):

        destination_path = request.POST.get('destination_path')
        file = request.FILES.get('file')

        return self.upload_file(file, destination_path)


    @retry(wait=wait_fixed(5), stop=stop_after_attempt(2))
    def upload_file(self, file, destination_path):
        ''' Upload a file in the Sharepoint destination path '''

        if is_token_expired(organization='sharepoint'):
            refresh_token(organization='sharepoint')

        token = get_actual_token(organization= 'sharepoint')

        filename = file.name

        url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFolderByServerRelativeUrl('{destination_path}')/Files/add(url='{filename}', overwrite=true)"

        headers = {
            'Accept': 'application/json;odata=verbose',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/octet-stream'
        }

        try:
            response = requests.post(url, headers=headers, data=file.read())
            response.raise_for_status()

        except Exception as e:
            raise Exception(f'Upload file error in {filename}: {e}')

        return Response(response.json(), status=response.status_code)


    def get(self, request, *args, **kwargs):
        ''' Get a sharepoint file in Bytes'''

        if is_token_expired(organization='graph'):
            refresh_token(organization='graph')

        token = get_actual_token(organization='graph')
        file_path = request.GET.get('file_path')

        unique_id = get_unique_id(file_path)

        if isinstance(unique_id, Response):
            return Response({'error': 'Not Found'}, status=404)

        return self.handle_sharepoint_request(token, unique_id)


    def fetch_sharepoint_content(self, token, unique_id, drive_id):
        '''
        Helper function to fetch content from SharePoint.

        - token: Sharepoint Authentication Token
        - unique_id: File unique id
        - drive_id: Sharepoint drive unique id

        - Return: File information from request
        '''

        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{unique_id}/content"
        headers = {
            'Accept': 'application/json;odata=verbose',
            'Authorization': f'Bearer {token}'
        }

        return requests.get(url, headers=headers)


    def handle_sharepoint_request(self, token, unique_id):
        '''
        Fetch content from primary drive, fallback to secondary if 404 is returned.

        - token: Sharepoint Authentication Token
        - unique_id: File unique id

        - Return: The process response for request
        '''

        # Try to fetch content from primary drive
        primary_response = self.fetch_sharepoint_content(token, unique_id, settings.SHAREPOINT_DRIVE_ID)

        if primary_response.status_code == 404:
            # Fallback to secondary drive if primary returns 404
            secondary_drive_id = ""
            secondary_response = self.fetch_sharepoint_content(token, unique_id, secondary_drive_id)

            return self.process_response(secondary_response)

        return self.process_response(primary_response)


    def process_response(self, response):
        '''
        Process the response and return the appropriate HttpResponse.
        '''

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            data = response.content

            return HttpResponse(data, content_type=content_type)
        else:
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
