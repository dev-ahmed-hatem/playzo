from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions


def enforce_csrf(request):
    """
    Enforce CSRF validation.
    """
    request.csrf_processing_done = False  # <-- Important!
    check = CSRFCheck(get_response=lambda req: None)  # dummy get_response
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)


class BaseAuthentication(JWTAuthentication):
    """Custom authentication class"""

    def authenticate(self, request):
        # First try to get the token from the Authorization header
        header = self.get_header(request)
        if header is None:
            # If no header, try to get the token from cookies
            raw_token = request.COOKIES.get("access_token")
        else:
            # If header is present, extract the token
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        ########## Deprecated ##########
        """
        not using csrf due to cross site domains
        """
        # Enforce CSRF protection if the token is from a cookie
        # if "access_token" in request.COOKIES:
        #     enforce_csrf(request)

        return self.get_user(validated_token), validated_token
