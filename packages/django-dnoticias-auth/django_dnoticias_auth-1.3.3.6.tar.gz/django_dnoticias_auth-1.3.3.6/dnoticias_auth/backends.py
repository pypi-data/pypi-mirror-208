import logging
import time
from typing import Optional

from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest
from django.db.models import Model
from django.urls import reverse

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from mozilla_django_oidc.utils import absolutify

from .utils import SessionManager

logger = logging.getLogger(__name__)


class ExtraClaimsOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims: dict) -> Model:
        """Return object for a newly created user account.

        :param claims: The OIDC claims.
        :return: The user object.
        :rtype: Model
        """

        email = claims.get('email')
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")
        is_staff = claims.get("is_staff", False)
        is_active = claims.get("is_active", True)
        is_superuser = claims.get("is_superuser", False)

        username = self.get_username(claims)

        return self.UserModel.objects.create_user(
            username,
            email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser
        )

    def update_user(self, user: Model, claims: dict) -> Model:
        """Update user account.

        :param user: The user object.
        :param claims: The OIDC claims.
        :return: The user object.
        :rtype: Model
        """
        has_changes = False

        data = {
            "email": claims.get('email'),
            "first_name": claims.get("given_name", ""),
            "last_name": claims.get("family_name", ""),
            "is_staff": claims.get("is_staff", False),
            "is_active": claims.get("is_active", True),
            "is_superuser": claims.get("is_superuser", False),
        }

        for field, value in data.items():
            if hasattr(user, field) and getattr(user, field) != value:
                setattr(user, field, value)
                has_changes = True

        if has_changes:
            user.save()

        return user

    def authenticate(self, request: HttpRequest, **kwargs) -> Optional[Model]:
        """Authenticates a user based on the OIDC code flow.

        :param request: The request object.
        :param kwargs: Additional keyword arguments.
        :return: The user object or None.
        :rtype: Optional[Model]
        """

        self.request = request
        if not self.request:
            return None

        state = self.request.GET.get('state')
        code = self.request.GET.get('code')
        nonce = kwargs.pop('nonce', None)

        if not code or not state:
            return None

        reverse_url = self.get_settings(
            'OIDC_AUTHENTICATION_CALLBACK_URL',
            'oidc_authentication_callback'
        )

        token_payload = {
            'client_id': self.OIDC_RP_CLIENT_ID,
            'client_secret': self.OIDC_RP_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': absolutify(
                self.request,
                reverse(reverse_url)
            ),
        }

        # Get the token
        token_info = self.get_token(token_payload)
        keycloak_session_id = token_info.get("session_state")
        id_token = token_info.get('id_token')
        access_token = token_info.get('access_token')
        refresh_token = token_info.get('refresh_token')
        expires_in = token_info.get('expires_in')
        refresh_expires_in = token_info.get('refresh_expires_in')

        # Validate the token
        payload = self.verify_token(id_token, nonce=nonce)
        keycloak_user_id = payload.get("sub")

        if payload:
            self.store_tokens(
                keycloak_session_id,
                access_token,
                id_token,
                refresh_token,
                expires_in,
                refresh_expires_in,
                keycloak_user_id
            )

            try:
                user = self.get_or_create_user(access_token, id_token, payload)

                if user:
                    session_manager = SessionManager(user.email)
                    session_manager.handle_event(
                        SessionManager.LOGIN,
                        keycloak_session_id,
                        self.request.session.get("old_keycloak_session_id"),
                    )
            except SuspiciousOperation as exc:
                logger.warning('failed to get or create user: %s', exc)
            else:
                return user

        return None

    def store_tokens(
        self,
        keycloak_session_id: str,
        access_token: str,
        id_token: str,
        refresh_token: str,
        expires_in: int,
        refresh_expires_in: int,
        keycloak_user_id: str,
    ):
        """Store OIDC tokens.

        :param keycloak_session_id: The keycloak session id.
        :param access_token: The access token.
        :param id_token: The id token.
        :param refresh_token: The refresh token.
        :param expires_in: The access token expiration time.
        :param refresh_expires_in: The refresh token expiration time.
        :param keycloak_user_id: The keycloak user id.
        """
        session = self.request.session
        session["keycloak_session_id"] = keycloak_session_id
        session["keycloak_user_id"] = keycloak_user_id

        if not session.get("old_keycloak_session_id"):
            session["old_keycloak_session_id"] = keycloak_session_id

        if self.get_settings('OIDC_STORE_ACCESS_TOKEN', False):
            session['oidc_access_token'] = access_token

        if self.get_settings('OIDC_STORE_ID_TOKEN', False):
            session['oidc_id_token'] = id_token

        if self.get_settings('OIDC_STORE_ACCESS_TOKEN_EXPIRATION', False):
            session['oidc_access_token_expiration'] = int(time.time()) + int(expires_in)

        if self.get_settings('OIDC_STORE_REFRESH_TOKEN_EXPIRATION', False):
            session['oidc_refresh_expires_in'] = refresh_expires_in

        if self.get_settings('OIDC_STORE_REFRESH_TOKEN', False):
            session['oidc_refresh_token'] = refresh_token
