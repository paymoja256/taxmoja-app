from django.http import HttpResponse
from django.shortcuts import render
from quickbooks import QuickBooks
from intuitlib.client import AuthClient
from django.http import HttpResponseRedirect

# Create your views here.
def connectToQuickbooks(request, client_acc_id):
    
    credentials = AuthClient(
            client_id='ABYwpAXd5JXEmxU9Uc96fVBTJWvv3SaETW0Dj4yPqwnUSA3PQY',
            client_secret='4JG4GnogLqGvDw4VrtRiDZN6BXacdGe7itZnJ4Dz',
            access_token='',  # If you do not pass this in, the Quickbooks client will call refresh and get a new access token. 
            environment='sandbox',
            redirect_uri='http://localhost:8000/callback',
        )

    print(credentials.__dict__)
    
    print(credentials.access_token)
    
    authorization_url = credentials.generate_url()
    # client_data.cred_state = credentials.state
    # client_data.save()
    # struct_logger.info(event='start_xero_auth_view', client_data=client_data.company_name, message='success')
    return HttpResponseRedirect(authorization_url)