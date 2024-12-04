# Standard Libraries
import requests

# Django
from django.conf import settings
from rest_framework.response import Response

# Memory
from io import BytesIO

# Utils
from sharepoint.utils.files import get_unique_id
#from MVPautomation.utils.utils_token import refresh_token, is_token_expired, get_actual_token


def get_file_size(file_data):
    '''
    Sends a request to the SharePoint file URL to retrieve its size.
    '''

    # SharePoint credentials
    if is_token_expired(organization='graph'):
        refresh_token(organization='graph')

    token = get_actual_token(organization='graph')

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # Mapping the file path
    file_path = file_data['webUrl'][41:]

    item_id = get_unique_id(file_path)

    url = f"https://graph.microsoft.com/v1.0/drives/{settings.SHAREPOINT_DRIVE_ID}/items/{item_id}/content"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_size = response.headers.get('Content-Length')

        return int(file_size) if file_size else None

    else:
        print(f"Error fetching file size: {file_path} {response.status_code}")
        return None


def get_files_from_library(library_name):
    '''
    Function to get all the files in a specific Library by Graph

    library_name: Library id to return the files
    '''

    # SharePoint credentials
    if is_token_expired(organization='graph'):
        refresh_token(organization='graph')

    token = get_actual_token(organization='graph')

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    # Get all files in the library
    files_data = []

    files_url = f"https://graph.microsoft.com/v1.0/sites/{settings.SHAREPOINT_SITE_ID}/lists/{library_name}/items"

    data = requests.get(files_url, headers=headers)

    if data.status_code == 200:

        data = data.json()

        # Validation to include only Documents
        for each in data['value']:
            if each['contentType']['name'] == 'Document':
                files_data.append(each)

        return files_data

    else:
        raise Exception(f"Error fetching files: {data.status_code}, {data.text}")


def get_sp_file(sharepoint_url):
    '''
    Function to get a specific file from Sharepoint to store in Memory and return it.
    '''

    # SharePoint credentials
    if is_token_expired(organization='sharepoint') is True:
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json;odata=verbose'
    }

    response = requests.get(sharepoint_url, headers=headers)

    if response.status_code == 200:
        sp_file = BytesIO(response.content)

        return sp_file
    else:
        raise Exception(f"Failed to download file: {response.status_code}, {response.text}")

