from django.http import JsonResponse,HttpResponseRedirect
from msal import ConfidentialClientApplication
import os
import requests

def my_view(request):
    return JsonResponse({"Hello": "World"})

def graph(request):
    try:
        scopes = ["https://graph.microsoft.com/.default"]
        downstream_api = "https://graph.microsoft.com/v1.0/me" #your downstream API resource endpoint
        current_access_token = request.headers.get("Authorization", None)
        
        # initialize the app
        app = ConfidentialClientApplication(
            client_id=os.environ.get("CLIENT_ID"),
            client_credential=os.environ.get("CLIENT_SECRET"),
            authority=f"https://login.microsoftonline.com/{os.environ.get("TENANT_ID")}"
        )

        #acquire token on behalf of the user that called this API
        downstream_api_access_token = app.acquire_token_on_behalf_of(
            user_assertion=current_access_token.split(' ')[1],
            scopes=scopes
        )

        if "access_token" in downstream_api_access_token:
            access_token = downstream_api_access_token["access_token"]
            # use access_token to call dowstream API e.g
            graphResponse = requests.get(downstream_api, headers={'Authorization': f'Bearer {access_token}'})
            return JsonResponse(graphResponse.json())
        elif "error" in downstream_api_access_token and (
            downstream_api_access_token.get("error") == "consent_required" or 
            downstream_api_access_token.get("suberror") == "consent_required"
            ):
            # Construct the consent URL
            consent_url = app.get_authorization_request_url(scopes, redirect_uri="http://localhost:3000")
            # Redirect the user to the consent URL
            return HttpResponseRedirect(consent_url)
        else:
            return JsonResponse({"error": downstream_api_access_token.get("error"),
                                 "error_description":downstream_api_access_token.get("error_description")}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)