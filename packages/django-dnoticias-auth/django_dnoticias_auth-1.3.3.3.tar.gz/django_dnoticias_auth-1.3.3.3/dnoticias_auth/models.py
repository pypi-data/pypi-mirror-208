import logging

import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser

logger = logging.getLogger(__name__)


class User(AbstractUser):
    def __str__(self):
        return self.email

    def get_roles(self):
        try:
            response = requests.get(settings.GET_ROLES_BY_EMAIL_URL, {"user_email" : self.email})
            response.raise_for_status()
            context = response.json()
            return context
        except:
            return []
