# Standard libraries
import requests

# Django
from django.conf import settings

# DRF
from rest_framework import status

# Utils
from sharepoint.utils.files import get_unique_id
# #from MVPautomation.utils.utils_token import get_actual_token, is_token_expired, refresh_token


def copy_file_by_id(file_id, destination_folder_url):
    '''
    Function to clone the files from Sharepoint into another folder by ID
    '''

    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/json'
    }

    api_url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/Web/GetFileById('{file_id}')/CopyTo(strNewUrl='{destination_folder_url}', bOverWrite=true)"

    try:
        response = requests.post(api_url, headers=headers)
        response.raise_for_status()
        return response.status_code, "File Copied Successfully"

    except requests.exceptions.RequestException as e:
        return status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)


def copy_file_to_destination(source_file_url, destination_folder_url):
    '''
    Function to search the File id and copy into the target folder
    '''

    file_id = get_unique_id(source_file_url)
    return copy_file_by_id(file_id, destination_folder_url)

