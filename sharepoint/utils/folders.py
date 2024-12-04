# Standard Libraries
import requests

# Django
from django.conf import settings

# Utils
#from MVPautomation.utils.utils_token import get_actual_token, is_token_expired, refresh_token


def create_folder(folder_path):
    ''' Create a folder in Sharepoint in the path receieve in request '''

    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    # Verify if the folder already exists
    if verify_folder_exists(folder_path):
        return True


    url = "https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/folders"

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


def verify_folder_exists(folder_path):
    ''' Verify if a folder exists in Sharepoint '''

    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')"

    headers = {
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return False

        return True
    except requests.exceptions.RequestException as e:
        print({'error': str(e)})
        raise Exception(f"Failed to verify if folder exists: {response.status_code}, {response.text}")


def count_files_in_folder (folder_path):
    ''' Count the number of files in a folder in Sharepoint '''

    if is_token_expired(organization='sharepoint'):
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFolderByServerRelativeUrl('{folder_path}')/Files"

    headers = {
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        files = data['d']['results']

        return len(files)
    except requests.exceptions.RequestException as e:
        print({'error': str(e)})
        raise Exception(f"Failed to count files in folder: {response.status_code}, {response.text}")
