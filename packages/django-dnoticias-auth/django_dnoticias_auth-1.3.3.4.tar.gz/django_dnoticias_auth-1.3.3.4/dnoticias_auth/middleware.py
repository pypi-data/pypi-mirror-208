import logging
import time
from urllib.parse import quote, urlencode
from re import Pattern

from django.http import HttpResponseRedirect, HttpRequest, JsonResponse, HttpResponse
from django.utils.module_loading import import_string
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import cached_property
from django.contrib.auth import BACKEND_SESSION_KEY
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse

import requests
from mozilla_django_oidc.utils import absolutify, add_state_and_nonce_to_session
from mozilla_django_oidc.middleware import SessionRefresh as SessionRefreshOIDC
from dnoticias_services.authentication.keycloak import get_user_keycloak_info
from mozilla_django_oidc.utils import absolutify, import_from_settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from .utils import set_cookie, SessionManager
from . import cookies_consts

User = get_user_model()
logger = logging.getLogger(__name__)


def get_refresh_redirect_url(request):
    OIDC_OP_AUTHORIZATION_ENDPOINT = import_from_settings('OIDC_OP_AUTHORIZATION_ENDPOINT')
    OIDC_RP_CLIENT_ID = import_from_settings('OIDC_RP_CLIENT_ID')
    OIDC_STATE_SIZE = import_from_settings('OIDC_STATE_SIZE', 32)
    OIDC_AUTHENTICATION_CALLBACK_URL = import_from_settings(
        'OIDC_AUTHENTICATION_CALLBACK_URL',
        'oidc_authentication_callback',
    )
    OIDC_RP_SCOPES = import_from_settings('OIDC_RP_SCOPES', 'openid email')
    OIDC_USE_NONCE = import_from_settings('OIDC_USE_NONCE', True)
    OIDC_NONCE_SIZE = import_from_settings('OIDC_NONCE_SIZE', 32)

    auth_url = OIDC_OP_AUTHORIZATION_ENDPOINT
    client_id = OIDC_RP_CLIENT_ID
    state = get_random_string(OIDC_STATE_SIZE)


    # Build the parameters as if we were doing a real auth handoff, except
    # we also include prompt=none.
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': absolutify(
            request,
            reverse(OIDC_AUTHENTICATION_CALLBACK_URL)
        ),
        'state': state,
        'scope': OIDC_RP_SCOPES,
        'prompt': 'none',
    }

    params.update(import_from_settings('OIDC_AUTH_REQUEST_EXTRA_PARAMS', {}))

    if OIDC_USE_NONCE:
        nonce = get_random_string(OIDC_NONCE_SIZE)
        params.update({
            'nonce': nonce
        })

    add_state_and_nonce_to_session(request, state, params)

    request.session['oidc_login_next'] = request.get_full_path()

    query = urlencode(params, quote_via=quote)

    return '{url}?{query}'.format(url=auth_url, query=query)


class BaseAuthMiddleware:
    @cached_property
    def exempt_url_patterns(self) -> set:
        """Urls that should not be processed by this middleware.
        This is a list of regular expressions.

        :return: set of regular expressions
        :rtype: set
        """
        exempt_patterns = set()

        for url_pattern in settings.AUTH_EXEMPT_URLS:
            if isinstance(url_pattern, Pattern):
                exempt_patterns.add(url_pattern)

        return exempt_patterns

    def _is_processable(self, request: HttpRequest):
        pass


class SessionRefresh(SessionRefreshOIDC):
    def is_refreshable_url(self, request: HttpRequest) -> bool:
        """Takes a request and returns whether it triggers a refresh examination

        :param request:
        :returns: boolean
        """
        # Do not attempt to refresh the session if the OIDC backend is not used
        backend_session = request.session.get(BACKEND_SESSION_KEY)
        is_oidc_enabled = True
        if backend_session:
            auth_backend = import_string(backend_session)
            is_oidc_enabled = issubclass(auth_backend, OIDCAuthenticationBackend)

        return (
            request.method == 'GET' and
            not any(pat.match(request.path) for pat in self.exempt_url_patterns) and
            request.user.is_authenticated and
            is_oidc_enabled and
            request.path not in self.exempt_urls
        )

    def process_request(self, request: HttpRequest) -> HttpResponse:
        """Takes a request and checks if it can be refreshed (redirects to keycloak silently).

        :param request: The request to be processed
        :returns: The response to the request
        :rtype: HttpResponse
        """
        if not self.is_refreshable_url(request):
            logger.debug('The request is not refreshable')
            return

        # This will use the keycloak token expiration saved in redis session instead of the
        # one saved in django session. This is because we need to refresh the keycloak token
        # for all django sessions instead of just one.
        expiration = request.session.get('oidc_id_token_expiration', 0)
        now = time.time()

        if expiration > now:
            # The id_token is still valid, so we don't have to do anything.
            logger.debug('id token is still valid (%s > %s)', expiration, now)
            return

        logger.debug('id token has expired')

        redirect_url = get_refresh_redirect_url(request)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Almost all XHR request handling in client-side code struggles
            # with redirects since redirecting to a page where the user
            # is supposed to do something is extremely unlikely to work
            # in an XHR request. Make a special response for these kinds
            # of requests.
            # The use of 403 Forbidden is to match the fact that this
            # middleware doesn't really want the user in if they don't
            # refresh their session.
            response = JsonResponse({'refresh_url': redirect_url}, status=403)
            response['refresh_url'] = redirect_url
            return response

        return HttpResponseRedirect(redirect_url)


class LoginCheckMiddleware(BaseAuthMiddleware, MiddlewareMixin):
    def _is_processable(self, request: HttpRequest):

        return (
            not any(pat.match(request.path) for pat in self.exempt_url_patterns)
            and not request.user.is_authenticated
            and request.COOKIES.get(cookies_consts.ACCESS_TOKEN)
        )

    def process_request(self, request: HttpRequest) -> HttpResponse:
        if not self._is_processable(request):
            return

        logger.debug(
            'User is not authenticated, but has an access token cookie, so redirecting to login'
        )
        redirect_url = get_refresh_redirect_url(request)
        response = HttpResponseRedirect(redirect_url)
        response.delete_cookie(cookies_consts.ACCESS_TOKEN)

        return response


class TokenMiddleware(BaseAuthMiddleware, MiddlewareMixin):
    """Just generates the cookie if the user is logged in"""
    def __init__(self, get_response):
        super(TokenMiddleware, self).__init__(get_response)

    def _is_processable(self, request: HttpRequest) -> bool:
        """Takes a request and checks if the path can be processed using the regex urls set

        :param request: The request to be processed
        :returns: True if the request can be processed, False otherwise
        :rtype: bool
        """
        return (
            not any(pat.match(request.path) for pat in self.exempt_url_patterns) and
            request.user.is_authenticated
        )

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Processes the response if the request can be processed. This will check if the
        user is logged in to set the cookies needed to make all the systems work.

        :param request: The request to be processed
        :param response: The response to the request
        :returns: The response to the request
        :rtype: HttpResponse
        """

        if self._is_processable(request):
            keycloak_session_cookie = cookies_consts.KC_SESSION_ID
            access_token_cookie = cookies_consts.ACCESS_TOKEN
            access_token_expiration_cookie = cookies_consts.ACCESS_TOKEN_EXPIRATION
            old_keycloak_session_cookie = cookies_consts.OLD_KC_SESSION_ID
            keycloak_user_id_cookie = cookies_consts.KC_USER_ID

            keycloak_session_value = request.session.get('keycloak_session_id', {})
            access_token_value = request.session.get('oidc_access_token', '')
            access_token_expiration_value = request.session.get('oidc_access_token_expiration', '')
            old_keycloak_session_value = request.session.get('old_keycloak_session_id', '')
            keycloak_user_id = request.session.get('keycloak_user_id', '')

            response = set_cookie(access_token_cookie, access_token_value, response, http_only=True)
            response = set_cookie(
                access_token_expiration_cookie,
                access_token_expiration_value,
                response,
                http_only=True
            )

            if keycloak_user_id:
                response = set_cookie(keycloak_user_id_cookie, keycloak_user_id, response)

            if keycloak_session_value:
                response = set_cookie(
                    keycloak_session_cookie,
                    keycloak_session_value,
                    response,
                    http_only=True
                )

            if old_keycloak_session_value != keycloak_session_value:
                request.session["old_keycloak_session_value"] = keycloak_session_value
                old_keycloak_session_value = keycloak_session_value

                session_manager = SessionManager(request.user.email)
                session_manager.handle_event(
                    SessionManager.UPDATE,
                    keycloak_session_value,
                    old_keycloak_session_value,
                )

                request.session.save()

            if old_keycloak_session_value:
                response = set_cookie(
                    old_keycloak_session_cookie,
                    old_keycloak_session_value,
                    response,
                    http_only=True
                )

        return response
