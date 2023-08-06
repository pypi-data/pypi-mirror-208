
import logging
from typing import Optional, Union

from django.conf import settings
from django.utils.encoding import force_str

import redis
from redis_sessions.session import RedisServer

from dnoticias_auth.exceptions import InvalidSessionParameters

logger = logging.getLogger(__name__)


class KeycloakSessionStorage:
    REDIS_PREFIX = settings.DJANGO_KEYCLOAK_ASSOC_REDIS

    def __init__(
        self,
        keycloak_session_id: str,
        django_session_id: Optional[str] = None,
        old_django_session_id: Optional[str] = None
    ):
        self.server = RedisServer(None).get()
        self.keycloak_session_id = keycloak_session_id
        self.django_session_id = django_session_id
        self.old_django_session_id = old_django_session_id

    def load(self) -> Union[str, dict]:
        """Loads the session data from redis

        :return: The session data
        :rtype: Union[str, dict]
        """
        try:
            session_data = self.server.get(self.get_real_stored_key())
            return force_str(session_data)
        except:
            return {}

    def custom_load(self, key: str) -> Union[dict, str]:
        """Loads a custom key from the session

        :param key: The key to load
        :type key: str
        :return: The value of the key
        :rtype: Union[dict, str]
        """
        try:
            session_data = self.server.get(key)
            return force_str(session_data)
        except:
            return {}

    def exists(self) -> bool:
        """Checks if the key exists in redis

        :return: True if exists, False otherwise
        :rtype: bool
        """
        return self.server.exists(self.get_real_stored_key())

    def create_or_update(self, session_data: Optional[dict]=dict()):
        """Creates or updates the session data on redis

        :param session_data: The session data
        :type session_data: Optional[dict]
        """
        if not self.django_session_id:
            raise InvalidSessionParameters("django_session_id is required for save/update")

        sessions = self.django_session_id
        logger.debug("Create or updating token %s", session_data)

        if self.exists():
            sessions = self.load()
            if self.old_django_session_id in sessions:
                sessions = sessions.replace(self.old_django_session_id, self.django_session_id)
            elif self.django_session_id not in sessions:
                sessions = f"{sessions},{self.django_session_id}"

            self.delete()

        self.save(sessions)

    def save(self, body: str):
        """Saves the session data on redis

        :param body: The session data
        :type body: str
        """
        logger.debug("Saving key: %s", self.keycloak_session_id)

        if redis.VERSION[0] >= 2:
            self.server.setex(
                self.get_real_stored_key(),
                self.get_expiry_age(),
                body
            )
        else:
            self.server.set(self.get_real_stored_key(), body)
            self.server.expire(self.get_real_stored_key(), self.get_expiry_age())

    def delete(self):
        """Deletes the session data from redis"""
        logger.debug("Deleting key: %s", self.keycloak_session_id)

        try:
            self.server.delete(self.get_real_stored_key())
        except:
            pass

    def get_real_stored_key(self) -> str:
        """Returns the key used to store the session data on redis

        :return: The key
        :rtype: str
        """
        return f"{self.REDIS_PREFIX}:{self.keycloak_session_id}"

    def get_expiry_age(self, **kwargs) -> int:
        """Returns the expiry age of the session data

        :return: The expiry age
        :rtype: int
        """
        return getattr(settings, "SESSION_REDIS_EXPIRATION", 3600 * 24 * 365)


class GenericSessionStorage:
    """This class is used to delete the session data from redis"""
    def __init__(self, key: str, expiration: Optional[int] = None):
        self.server = RedisServer(None).get()
        self.key = key
        self.expiration = expiration or 60 * 60 * 60

    def load(self) -> Union[dict, str]:
        try:
            session_data = self.server.get(self.key)
            return force_str(session_data) if session_data else {} 
        except Exception as e:
            return {}

    def delete(self):
        """Deletes the session data from redis"""
        logger.debug("Deleting key: %s", self.key)

        try:
            self.server.delete(self.key)
        except:
            pass

    def get_real_stored_key(self) -> str:
        return self.key

    def get_expiry_age(self, **kwargs) -> int:
        """Returns the expiry age of the session data

        :return: The expiry age
        :rtype: int
        """
        return self.expiration

    def save(self, body: str):
        """Saves the session data on redis

        :param body: The session data
        :type body: str
        """
        if redis.VERSION[0] >= 2:
            self.server.setex(self.get_real_stored_key(), self.get_expiry_age(), body)
        else:
            self.server.set(self.get_real_stored_key(), body)
            self.server.expire(self.get_real_stored_key(), self.get_expiry_age())
