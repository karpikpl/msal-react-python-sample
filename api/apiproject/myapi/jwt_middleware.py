import jwt
from django.http import JsonResponse
import json
import os
import logging

logger = logging.getLogger(__name__)

TENANT_ID = os.environ.get("TENANT_ID")
API_AUDIENCE = os.environ.get("API_AUDIENCE")


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        authorization_header = request.headers.get("Authorization", None)

        if not authorization_header:
            return JsonResponse(
                {"error": "Authorization header is missing"}, status=401
            )

        parts = authorization_header.split()

        if parts[0].lower() != "bearer":
            return JsonResponse(
                {
                    "code": "invalid_header",
                    "description": "Authorization header must start with" " Bearer",
                },
                status=401,
            )
        elif len(parts) == 1:
            return JsonResponse(
                {"code": "invalid_header", "description": "Token not found"}, status=401
            )
        elif len(parts) > 2:
            return JsonResponse(
                {
                    "code": "invalid_header",
                    "description": "Authorization header must be" " Bearer token",
                },
                status=401,
            )

        token = parts[1]

        try:
            # decode without signature verification
            # verify audience and issuer
            docoded = jwt.decode(token, options={"verify_signature": False})

            # verify audience and issuer
            if docoded["aud"] != API_AUDIENCE:
                return JsonResponse(
                    {
                        "code": "invalid_audience",
                        "description": "Token audience is invalid",
                    },
                    status=401,
                )
            
            if docoded["iss"] != "https://sts.windows.net/" + TENANT_ID + "/":
                return JsonResponse(
                    {
                        "code": "invalid_issuer",
                        "description": "Token issuer is invalid",
                    },
                    status=401,
                )

            # ideally, we would cache the keys
            jwks_client = jwt.PyJWKClient(
                "https://login.microsoftonline.com/"
                + TENANT_ID
                + "/discovery/v2.0/keys"
            )

            unverified_header = jwt.get_unverified_header(token)

            rsa_key = jwks_client.get_signing_key(unverified_header["kid"]).key
        except Exception as e:
            return JsonResponse(
                {
                    "code": "invalid_header",
                    "description": "Unable to parse authentication" " token.",
                    "details": str(e),
                },
                status=401,
            )

        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=API_AUDIENCE,
                    issuer="https://sts.windows.net/" + TENANT_ID + "/",
                    verify=True,
                    options={
                        "verify_exp": True,
                        "verify_nbf": True,
                        "verify_iat": True,
                        "verify_aud": True,
                        "verify_iss": True,
                    },
                )

                # Add decoded token to request if needed
                request.user_info = payload
            except jwt.ExpiredSignatureError:
                return JsonResponse(
                    {"code": "token_expired", "description": "token is expired"},
                    status=401,
                )
            except jwt.MissingRequiredClaimError:
                return JsonResponse(
                    {
                        "code": "invalid_claims",
                        "description": "incorrect claims,"
                        "please check the audience and issuer",
                    },
                    status=401,
                )
            except Exception as e:
                logger.error(f"Error in JWTAuthenticationMiddleware: {e}")
                return JsonResponse(
                    {"code": "invalid_header", "description": str(e)}, status=401
                )
        else:
            return JsonResponse(
                {
                    "code": "invalid_header",
                    "description": "Unable to find appropriate key",
                },
                status=401,
            )

        # check scopes ?
        logger.info(f"Payload: {request.user_info}")

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
