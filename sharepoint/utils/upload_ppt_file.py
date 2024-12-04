# Standard Libraries
import json
import os
import requests
import itertools

# Django
from django.conf import settings


# Memory
from io import BytesIO

# Models
#from MVPautomation.project.models import MethodologyModel
#from MVPautomation.users.models import User

# Django
from django.http import HttpResponse
from rest_framework.response import Response


# Office Libraries
from pptx.util import Pt
from pptx import Presentation
from office365.sharepoint.files.file import File

# Utils
#from MVPautomation.utils.utils_token import refresh_token, is_token_expired, get_actual_token


def upload_ppt_file(sharepoint_upload_url, modified_file):

    '''
    Function to update "upload" a ppt file in Sharepoint.
    '''

    if is_token_expired(organization='sharepoint') is True:
            refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    }

    response = requests.put(sharepoint_upload_url, headers=headers, data=modified_file)

    if response.status_code == 204:
        print("File uploaded successfully.")

    elif response.status_code == 423:
        data = json.loads(response.content)
        error = data['error']['message']['value']
        raise Exception(f"File is still opened: {response.status_code}, {error}")
    else:
        raise Exception(f"Failed to upload file: {response.status_code}, {response.text}")


def upload_doc_file(sharepoint_upload_url, modified_file, filename):

    '''
    Function to update "upload" a doc file in Sharepoint.
    '''

    if is_token_expired(organization='sharepoint') is True:
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/octet-stream'
    }

    response = requests.post(sharepoint_upload_url, headers=headers, data=modified_file)

    if response.status_code == 200:
        if filename != "":
            os.remove(filename)
        print("File uploaded successfully.")
        return response.json().get('d').get('LinkingUri')


    elif response.status_code == 423:
        if filename != "":
            os.remove(filename)
        data = json.loads(response.content)
        error = data['error']['message']['value']
        raise Exception(f"File is still opened: {response.status_code}, {error}")
    else:
        if filename != "":
            os.remove(filename)
        raise Exception(f"Failed to upload file: {response.status_code}, {response.text}")


def upload_xlsx_file(sharepoint_upload_url, modified_file):

    '''
    Function to update "upload" an xlsx file in Sharepoint.
    '''

    if is_token_expired(organization='sharepoint') is True:
        refresh_token(organization='sharepoint')

    token = get_actual_token(organization='sharepoint')

    headers = {
        'Authorization': f'Bearer {token}', 
        'Accept': 'application/json;odata=verbose',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 

    }

    response = requests.post(sharepoint_upload_url, headers=headers, data=modified_file)

    if response.status_code == 200:
        print("File uploaded successfully.")
        return response.json().get('d').get('LinkingUri')

    elif response.status_code == 423:
        data = json.loads(response.content)
        error = data['error']['message']['value']
        raise Exception(f"File is still opened: {response.status_code}, {error}")
    else:
        raise Exception(f"Failed to upload file: {response.status_code}, {response.text}")