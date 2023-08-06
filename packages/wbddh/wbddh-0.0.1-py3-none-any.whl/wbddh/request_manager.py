import requests
from .exceptions import *

public_API_URL = "https://ddhoutboundapiuat.asestg.worldbank.org"

def get(endpoint, params=None, headers=None, session=None):
    '''Send a GET request

    Arguments:
        endpoint:		the endpoint (e.g., "datasets")
        params:			parameters
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    if session:
        session.check_tokens()
        return requests.get(get_endpoint(endpoint, session), params=params, verify=session.verify, headers=session.get_headers(headers))
    else:
        return requests.get(get_endpoint(endpoint), params=params)



def post(endpoint, params=None, json=None, headers=None, session=None):
    '''Send a POST request

    Arguments:
        endpoint:		the endpoint (e.g., "dataset/listpage")
        json:			data object
        params:			query parameters
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    if session:
        session.check_tokens()
        try:
            response = requests.post(get_endpoint(endpoint, session), params=params, json=json, verify=session.verify, headers=session.get_headers(headers))
        except requests.ConnectionError as e:
            raise requests.ConnectionError(e.response)
        except requests.exceptions.RequestException as e:
            raise requests.ConnectionError(e.response)
        return response
    else:
        raise DDHSessionException("DDH POST request requires a session")



def post_file(endpoint, files=None, headers=None, session=None):
    '''Send a POST request with file

    Arguments:
        endpoint:		the endpoint (e.g., "dataset/listpage")
        files:			multi-part form object
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    if session:
        session.check_tokens()
        return requests.post(get_endpoint(endpoint, session), files=files, verify=session.verify, headers=session.get_headers(headers))
    else:
        raise DDHSessionException("DDH POST request requires a session")


def get_endpoint(endpoint, session=None):
    if session:
        return '/'.join([session.api_host, endpoint])
    else:
        return '/'.join([public_API_URL, endpoint])