# Standard Libraries
import os
from django.views import View
import requests
import json

# Django
from django.conf import settings

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Permissions
from rest_framework.permissions import AllowAny

# Utils
#from MVPautomation.utils.utils_token import refresh_token


class SharepointAuthorizationRefreshAPIView(APIView):

    ''' Class view for Sharepoint API '''

    permission_classes = [AllowAny]

    def get(self, request):
        refresh_token(organization='sharepoint')
        return Response({'message': 'Token refreshed'}, status=status.HTTP_200_OK)
