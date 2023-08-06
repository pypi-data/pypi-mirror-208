def API_factory(service_type):
    if service_type == 'graph':
        from . microsoft.GraphAPI import GraphAPI
        return GraphAPI()
    if service_type == 'azure':
        from . microsoft.AzureAPI import AzureAPI
        return AzureAPI()
    if service_type == 'salesforce':
        from . salesforce.SalesForceAPI import SalesForceAPI 
        return SalesForceAPI()
    if service_type == 'gcp':
        from . google.GCPAPI import GCPAPI
        return GCPAPI()
    if service_type == 'google_workspace':
        from . google.GoogleWorkspaceAPI import GoogleWorkspaceAPI
        return GoogleWorkspaceAPI()
    if service_type == 'adobe':
        from . adobe.AdobeAPI import AdobeAPI
        return AdobeAPI()
        
