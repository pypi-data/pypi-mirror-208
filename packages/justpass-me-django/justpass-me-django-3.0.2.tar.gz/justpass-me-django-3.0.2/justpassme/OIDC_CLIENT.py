from urllib.parse import urlencode

from django.contrib import auth
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from jose import jwt
from mozilla_django_oidc.utils import absolutify, add_state_and_nonce_to_session
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, get_next_url, OIDCAuthenticationCallbackView

from django.conf import settings

from mozilla_django_oidc.auth import OIDCAuthenticationBackend, LOGGER



class Authenticate(OIDCAuthenticationRequestView):
    """Prepares the parameters to redirect to authorize endpoint"""
    def get(self, request):
        """OIDC client authentication initialization HTTP endpoint"""
        state = get_random_string(self.get_settings("OIDC_STATE_SIZE", 32))
        redirect_field_name = self.get_settings("OIDC_REDIRECT_FIELD_NAME", "next")
        reverse_url = self.get_settings(
            "OIDC_AUTHENTICATION_CALLBACK_URL", "oidc_authentication_callback"
        )

        params = {
            "response_type": "code",
            "scope": self.get_settings("OIDC_RP_SCOPES", "openid email"),
            "client_id": self.OIDC_RP_CLIENT_ID,
            "redirect_uri": absolutify(request, reverse(reverse_url)),
            "state": state,
        }

        params.update(self.get_extra_params(request,state))

        if self.get_settings("OIDC_USE_NONCE", True):
            nonce = get_random_string(self.get_settings("OIDC_NONCE_SIZE", 32))
            params.update({"nonce": nonce})

        add_state_and_nonce_to_session(request, state, params)

        request.session["oidc_login_next"] = get_next_url(request, redirect_field_name)

        query = urlencode(params)
        redirect_url = "{url}?{query}".format(
            url=self.OIDC_OP_AUTH_ENDPOINT, query=query
        )
        print(redirect_url)
        return HttpResponseRedirect(redirect_url)

    def get_extra_params(self, request,state):
        if request.user.is_authenticated:
            token = getattr(request.user,getattr(settings,"OIDC_USERNAME_FIELD","username"))
        else:
            token = request.session.get("token")
        v = {"state": state}
        d = {}
        if token:
            d["login_hint"]= token
            d["username"] = token
            v["login_hint"]= token

        prompt = "login"
        if request.session.get("JP_OP_MODE") == "REG":
            prompt="create"
        signature = jwt.encode(v,settings.OIDC_RP_CLIENT_SECRET,'HS256')
        d.update({"hint_mode":"token" ,"acr_values":"keys","max_age":60,"signature":signature,
             "prompt":prompt})
        if request.META.get("HTTP_AMWAL_PLATFORM"):
            d["AMWALPLATFORM"] = request.META.get("HTTP_AMWAL_PLATFORM","")
            request.session["AMWALPLATFORM"] = d["AMWALPLATFORM"]
        return d


class AuthenticationView(OIDCAuthenticationRequestView):
    def verify_claims(self, claims):
        """Verify the provided claims to decide if authentication should be allowed."""

        # Verify claims required by default configuration
        scopes = self.get_settings("OIDC_RP_SCOPES", "openid profile")


        LOGGER.warning(
            "Custom OIDC_RP_SCOPES defined. "
            "You need to override `verify_claims` for custom claims verification."
        )

        return True

class OIDCUserFinder(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        username  = claims.get("preferred_username")
        User = auth.get_user_model()
        try:
            kwargs = {getattr(settings,"OIDC_USERNAME_FIELD","username"): username}
            profile = User.objects.get(**kwargs)
            return [profile]
        except Exception: pass
        return self.UserModel.objects.none()


class Callback(OIDCAuthenticationCallbackView):
    """Handles the callback received from OIDC Provider"""
    def get(self, request):
        """Callback handler for OIDC authorization code flow"""

        if request.GET.get("error"):
            # Ouch! Something important failed.

            # Delete the state entry also for failed authentication attempts
            # to prevent replay attacks.
            if (
                "state" in request.GET
                and "oidc_states" in request.session
                and request.GET["state"] in request.session["oidc_states"]
            ):
                del request.session["oidc_states"][request.GET["state"]]
                request.session.save()

            # Make sure the user doesn't get to continue to be logged in
            # otherwise the refresh middleware will force the user to
            # redirect to authorize again if the session refresh has
            # expired.
            # if request.user.is_authenticated:
            #     auth.logout(request)
            # assert not request.user.is_authenticated
        elif "code" in request.GET and "state" in request.GET:

            # Check instead of "oidc_state" check if the "oidc_states" session key exists!
            if "oidc_states" not in request.session:
                return self.login_failure()

            # State and Nonce are stored in the session "oidc_states" dictionary.
            # State is the key, the value is a dictionary with the Nonce in the "nonce" field.
            state = request.GET.get("state")
            if state not in request.session["oidc_states"]:
                msg = "OIDC callback state not found in session `oidc_states`!"
                raise SuspiciousOperation(msg)

            # Get the nonce from the dictionary for further processing and delete the entry to
            # prevent replay attacks.
            nonce = request.session["oidc_states"][state]["nonce"]
            del request.session["oidc_states"][state]
            op_mode = request.session.get("OP_MODE")
            # Authenticating is slow, so save the updated oidc_states.
            request.session.save()
            # Reset the session. This forces the session to get reloaded from the database after
            # fetching the token from the OpenID connect provider.
            # Without this step we would overwrite items that are being added/removed from the
            # session in parallel browser tabs.
            request.session = request.session.__class__(request.session.session_key)

            kwargs = {
                "request": request,
                "nonce": nonce,
            }

            self.user = auth.authenticate(**kwargs)
            request.session["OP_MODE"] = op_mode
            if self.user and self.user.is_active:
                return self.login_success()
        return self.login_failure()