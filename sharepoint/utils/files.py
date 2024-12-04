# Standart Libraries
import io
import json
import requests

# DRF
from rest_framework.response import Response
from rest_framework import status

# Utils
# #from MVPautomation.utils.utils_token import get_actual_token, is_token_expired, refresh_token


def get_unique_id(folder_path):
    ''' Function to Get the Unique Id of a specific file in folder'''

    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFileByServerRelativeUrl('{folder_path}')"

    headers = {
        'Accept': 'application/json;odata=verbose',
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers)
        # Parse JSON response
        response_data = response.json()
        unique_id = response_data.get('d', {}).get('UniqueId')
        if unique_id:
            return unique_id
        else:
            return Response({'error': 'Unique Id not found'}, status=status.HTTP_404_NOT_FOUND)


    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except json.JSONDecodeError as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except KeyError as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TODO: UNUSED FUNCTIONALITY PENDING TO IMPROVE OR UPDATE IF NEEDED
def delete_file_by_id(file_id):
    """
    Delete a file by its ID.
    """
    # Check if the SharePoint token is expired and refresh it if necessary
    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')

    # Get the current SharePoint token
    token = get_actual_token(organization='sharepoint')

    # Define the URL for the file deletion request
    url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFileById('{file_id}')"
    headers = {
        'Accept': 'application/json;odata=verbose',
        'Authorization': f'Bearer {token}'
    }

    try:
        # Send a DELETE request to the SharePoint API
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return Response({'message': 'File deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_file_by_path(destiantion_path, file_path):
    ''' Create a file in the destination path '''

    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    file_content = None
    with open(file_path, 'rb') as f:
        file_content = f.read()

    filename = file_path.split('/')[-1]


    url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFolderByServerRelativeUrl('{destiantion_path}')/Files/add(url='{filename}', overwrite=true)"
    headers = {
        'Accept': 'application/json;odata=verbose',
        'Authorization': f'Bearer {token}',  # Replace {your_access_token} with your actual access token
        'Content-Type': 'image/jpeg'
    }
    try:
        response = requests.post(url, headers=headers, data=file_content)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(response.json(), status=response.status_code)
