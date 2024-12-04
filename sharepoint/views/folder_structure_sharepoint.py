# Standard Libraries
import json
import requests

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Views
from sharepoint.views.folders_sharepoint import SharePointFolderView


class FolderStructureSharepointView(APIView):

    def post(self, request, *args, **kwargs):
        ''' Create a folder in Sharepoint in the path receieve in request '''

        # Get data from the POST body request
        data = json.loads(request.body)
        folder_path = data.get('folder_path')

        if folder_path is None:
            return Response({'message': 'Folder path is required'}, status=status.HTTP_400_BAD_REQUEST)

        return self.create_structure(folder_path=folder_path)


    def create_structure(self, folder_path):
        # Define the folder structure
        folders = [
            { "1.0 PMO": ["Calendar", "Suppliers"] },
            "2.0 RFI",
            { "3.0 Interviews": ["Consumer", "Experts", "Internal"] },
            "4.0 Surveys",
            "5.0 Field Visits",
            "6.0 Presentations",
            "5.0 Closing minutes",
            "6.0 Contracts"
        ]

        try:
            folder_sharepoint_view = SharePointFolderView()

            for folder in folders:
                if isinstance(folder, str):
                    # Create the main folder
                    path = f"{folder_path}/{folder}"
                    folder_sharepoint_view.create_folder(path)
                else:
                    # Create the main folder and its subfolders
                    for key, value in folder.items():
                        main_folder = key
                        main_folder_path = f"{folder_path}/{main_folder}"
                        folder_sharepoint_view.create_folder(main_folder_path)

                        for subfolder in value:
                            subfolder_path = f"{main_folder_path}/{subfolder}"
                            folder_sharepoint_view.create_folder(subfolder_path)

            return Response({'message': 'Folders created successfully'}, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            return Response({'Folder creation error: ': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
