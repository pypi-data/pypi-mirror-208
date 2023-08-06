from django.urls import path
from . import views


urlpatterns = [
    path(
        'silent-check-sso/',
        views.SilentCheckSSOView.as_view(),
        name="silent-check-sso"
    ),
    path(
        'logout/',
        views.DnoticiasOIDCLogoutView.as_view(),
        name="dnoticias-auth-logout"
    ),
    path(
        'callback/',
        views.DnoticiasOIDCAuthenticationCallbackView.as_view(),
        name="dnoticias-auth-callback"
    ),
    path(
        'app/data/',
        views.ApplicationDataView.as_view(),
        name="application-data"
    ),
    path(
        "endpoints/logout/",
        views.DnoticiasLogoutEndpointView.as_view(),
        name="dnoticias-logout-endpoint"
    ),
    path(
        "verify/",
        views.SendVerificationEmailView.as_view(),
        name="dnoticias-auth-verify"
    )
]
