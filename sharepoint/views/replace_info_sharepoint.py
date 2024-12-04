# Standard Libraries
import json

# Django
from django.conf import settings


# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Memory
from io import BytesIO

# Models
# from MVPautomation.project.models import ActivityDetailsModel

# Office Libraries
from pptx import Presentation

# Permissions
from rest_framework.permissions import AllowAny

# Utils
from sharepoint.utils import (
    modify_sp_file, get_sp_file, upload_ppt_file, include_proposal_info_ppt,
    include_json_into_ppt, delete_slide_by_tittle, add_images_s3_ppt, create_gantt,
    populate_versioning
)
from sharepoint.utils.include_images import include_logo


class FileUpdateSharepointAPIView(APIView):

    ''' Class view for Replace information in a PPTX file store in Sharepoint '''

    permission_classes = [AllowAny]


    def post(self, request):

        # Get data from the POST body request
        data = json.loads(request.body)
        file_path  = data.get('file_path')

        # Get the file path from Sharepoint
        sharepoint_url = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFileByServerRelativeUrl('{file_path}')/$value"

        try:
            # Save the file in Memory to work without the need of downloading
            file_in_memory = get_sp_file(sharepoint_url)
            presentation = Presentation(file_in_memory)

        except Exception as e:
            return Response({"error": f"Failed to open presentation: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Functionality to include logo in PPTX
        try:
            # Logo
            file_path = file_path.split("/")[:-1]
            logo_path = "/".join(file_path) + "/logo.png"
            logo_path = f"https://{settings.sharepoint_path}/sites/{your-organization-name}/_api/web/GetFileByServerRelativeUrl('{logo_path}')/$value"

            include_logo(presentation, logo_path)
        except Exception as e:
            print(f"The Logo couldn't be included: {e}")

        actions = ['versioning', 'team', 'proposal', 'slides_data', 'methodology', 'delete']

        for action in actions:
            if action in data:
                self.populate_ppt_sections(action, data, presentation)

        # Save the modified presentation to an in-memory buffer
        modified_file = BytesIO()
        presentation.save(modified_file)
        modified_file.seek(0)

        # Upload the updated file to Sharepoint
        upload_ppt_file(sharepoint_url, modified_file)

        return Response({'message': 'PPTX file modified and uploaded successfully'}, status=status.HTTP_200_OK)


    def populate_ppt_sections(self, action, data, presentation):
        '''
        Function to populate the different section of pptx presentation based on the information in DB

        - action: Action to perfomed
        - data: JSON with the data sent in the POST
        - presentation: pptx Document saved in Memory

        Return: No action returned
        '''

        if action == 'versioning':
            version_info = data.get('versioning')
            populate_versioning(presentation, version_info)

        if action == 'team':
            team = data.get('team')
            if 'introduce_team' in team:
                add_images_s3_ppt(presentation, team)

            include_json_into_ppt(presentation, team)

        if action == 'proposal':
            proposal_id = data.get('proposal')
            include_proposal_info_ppt(presentation, proposal_id)

        if action == 'slides_data':
            json_instance = data.get('slides_data')
            include_json_into_ppt(presentation, json_instance)

        if action == 'methodology':
            # Get data from body request and search the instance
            id_method = data.get('methodology')

            # activity_info = ActivityDetailsModel.objects.filter(methodology_id=id_method)
            # activity_info_slide = activity_info.filter(is_slide=True)

            # create_gantt(presentation, activity_info)
            # modify_sp_file(presentation, activity_info_slide, id_method)

        if action == 'delete':
            # Delete the selected slides from Presentation
            slides = data.get('delete')
            delete_slide_by_tittle(presentation, slides)
