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
# from utils.utils_token import is_token_expired, refresh_token, get_actual_token


class SharePointFolderView(APIView):

    def get(self, request, *args, **kwargs):
        ''' Get all files in the folder path provided '''

        if is_token_expired(organization='sharepoint'):
            refresh_token('sharepoint')

        token = get_actual_token(organization='sharepoint')
        folder_path = request.GET.get('folder_path')

        url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/Web/GetFolderByServerRelativePath(decodedurl='{folder_path}')/Files"

        headers = {
            'Accept': 'application/json;odata=verbose',
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Parse JSON response
            response_data = response.json()
            results = response_data.get('d', {}).get('results')

            if results:
                return Response(results, status=response.status_code)
            else:
                return Response(response_data, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except json.JSONDecodeError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request, *args, **kwargs):
        ''' Create a folder in Sharepoint in the path receieve in request '''

        data = json.loads(request.body)
        folder_path = data.get('folder_path')

        if folder_path is None:
            return Response({'message': 'Folder path is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if self.create_folder(folder_path=folder_path):
                return Response({'message': 'Folder created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Failed to create folder'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create_folder(self, folder_path):
        ''' Create a folder in Sharepoint in the path receieve in request '''

        if is_token_expired(organization='sharepoint'):
            refresh_token(organization='sharepoint')

        token = get_actual_token(organization='sharepoint')

        url = "https://{settings.sharepoint_path}/sites/iotaimpact/_api/web/folders"

        headers = {
            'Accept': 'application/json;odata=verbose',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        payload = {
            'ServerRelativeUrl': folder_path
        }

        folders = folder_path.split('/')[1:]

        static_path = ""

        for i in folders[:3]:
            if i is not None or i != "":
                static_path = f'{static_path}/{i}'

        folders = folders[3:]

        for folder in folders:
            static_path = f'{static_path}/{folder}'
            payload['ServerRelativeUrl'] = static_path

            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()

            except requests.exceptions.RequestException as e:
                print({'error': str(e)})
                return False

        return True
