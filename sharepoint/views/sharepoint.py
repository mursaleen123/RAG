# Standard Libraries
import os
import requests
import json

# Django
from django.conf import settings

# DRF
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import AllowAny

# Utils
#from MVPautomation.utils.utils_token import get_token


class SharepointAuthorizationAPIView(APIView):

    ''' Class view for Sharepoint API authentication'''

    permission_classes = [AllowAny]

    def get(self):
        if get_token(organization='sharepoint'):
            return Response({'message': 'Token refreshed'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to obtain access token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)