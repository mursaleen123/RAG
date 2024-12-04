# Standard libraries
import requests

# Django
from django.conf import settings


# DRF
from rest_framework import status

# Utils
#from MVPautomation.sharepoint.utils.files import get_unique_id
#from MVPautomation.utils.utils_token import get_actual_token, is_token_expired, refresh_token


def move_file_by_id(file_id, destination_folder_url):
    '''
    Function to move file between folders in Sharepoint
    '''

    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/json'
    }

    api_url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/Web/GetFileById('{file_id}')/MoveTo(newUrl='{destination_folder_url}')"
    try:
        response = requests.post(api_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.status_code, "File Moved Successfully"

    except requests.exceptions.RequestException as e:
        return status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)


def move_file_to_destination(source_file_url, destination_folder_url):
    file_id = get_unique_id(source_file_url)
    return move_file_by_id(file_id, destination_folder_url)


def get_valid_token():
    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')
    return get_actual_token(organization='sharepoint')
