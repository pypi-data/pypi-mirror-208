import os
import sys
import msal
import yaml
from datetime import datetime, timedelta
import logging
import json
from .utils import *
from .exceptions import *

class DDHSession():
	def __init__(self, name, app, token, api_host, verify=None, refresh='auto'):
		self.token = token
		self.name = name
		self.verify = verify
		self.refresh = refresh
		self.application = app
		self.scopes = list(token['scope'].split(" "))
		self.api_host = api_host
		self.headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
		self.expires_on = datetime.now() + timedelta(seconds=token['expires_in'])

	def __repr__(self):
		return 'DDH2Session(host="{}", user_name="{}", expires="{}")'.format(self.host,
																			 self.token['id_token_claims']['preferred_username'],
																			 self.expires_on)

	def get_headers(self, headers=None):

		if headers:
			http_headers = self.headers.copy()
			http_headers.update(headers)
			return http_headers

		return self.headers

	def copy_token(self):
		''' Copies the authentication token to the clipboard.
        This is helpful for testing endpoints in Postman or another web tool
        '''
		return copy_to_clipboard(self.headers['Authorization'])

	def check_tokens(self, refresh=None):
		'''Refreshes access tokens if they have expired. This should be called prior to any API call.

        Arguments:
            refresh:		'auto', 'never', or 'always'
        '''
		if refresh == None:
			refresh = self.refresh

		if refresh == 'never' or (refresh == 'auto' and (datetime.now() + timedelta(seconds=3)) < self.expires_on):
			return

		logging.info('access_token has expired; requesting a new one')
		accounts = self.application.get_accounts()
		# Assuming the end user is using the first one
		new_token = self.application.acquire_token_silent(self.scope, account=accounts[0])

		self.token = new_token
		self.headers['Authorization'] = 'Bearer {}'.format(new_token['access_token'])
		self.expires_on = datetime.now() + timedelta(seconds=new_token['expires_in'])



def create_session(name='default_ddh_session', params=None, autoCopy=True, verify=None):
	defaults = {
		"authorityHostURL": "https://login.microsoftonline.com",
		"clientId": None,
		"tenant": None,
		"resourceURL": None,
		"apiHostURL": None
	}

	# sanity check
	for key in defaults.keys():
		if not params[key]:
			raise ValueError('{} must be a defined config parameter'.format(key))

	authority = '/'.join([params['authorityHostURL'], params['tenant']])
	scopes = [params['resourceURL'] +  '/.default']
	api_host = params['apiHostURL']

	app = msal.PublicClientApplication(
		params["clientId"], authority=authority,
		# token_cache=...  # Default cache is in memory only.
						   # You can learn how to use SerializableTokenCache from
						   # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
	)

	# Acquire a token
	token = None

	# Check the cache to see if this end user has signed in before
	accounts = app.get_accounts()
	if accounts:
		logging.info("Account(s) exists in cache, probably with token too. Let's try.")
		print(f"try to find a token in cache for account: {accounts[0]}")
		token = app.acquire_token_silent(scopes=scopes, account=accounts[0])

	if not token:
		logging.info("No suitable token exists in cache. Let's get a new one.")
		flow = app.initiate_device_flow(scopes=scopes)
		if "user_code" not in flow:
			raise ValueError(
				"Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

		print(flow["message"])
		if autoCopy and copy_to_clipboard(flow['user_code']):
			print('The code has been copied to your clipboard')
		token = app.acquire_token_by_device_flow(flow)  # By default it will block
		
	if "access_token" in token:
		return DDHSession(name, app, token, api_host, verify)
	else:
		raise DDHAuthenticationException(token)



def create_service_account_session(name='default_ddh_session', params=None, verify=None):
	import msal
	defaults = {
		"authorityHostURL": "https://login.microsoftonline.com",
		"clientId": None,
		"tenant": None,
		"resourceURL": None,
		"apiHostURL": None,
		'username': None,
		'password': None
	}

	if params is None:
		path = os.path.join(os.path.expanduser('~'), '.ddh_config.yaml')
		with open(path, 'r') as fd:
			yaml_file = yaml.safe_load(fd)

		config = yaml_file.get(name, {})
		if not config:
			raise ValueError('No config information for {} in {}'.format(name, path))

		params = defaults.copy()
		params.update(config)

	# sanity check
	for key in defaults.keys():
		if not params[key]:
			raise ValueError('{} must be a defined config parameter'.format(key))

	authority_url = '/'.join([params['authorityHostURL'], params['tenant']])
	scopes = [params['resourceURL'] +  '/.default']
	api_host = params['apiHostURL']

	app = msal.PublicClientApplication(
		params["clientId"], authority=authority_url,
		# token_cache=...  # Default cache is in memory only.
		# You can learn how to use SerializableTokenCache from
		# https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
	)

	# Acquire a token
	token = None

	# Firstly, check the cache to see if this end user has signed in before
	accounts = app.get_accounts(username=params["username"])
	if accounts:
		logging.info("Account(s) exists in cache, probably with token too. Let's try.")
		token = app.acquire_token_silent(scopes=scopes, account=accounts[0])

	if not token:
		logging.info("No suitable token exists in cache. Let's get a new one.")
		# See this page for constraints of Username Password Flow.
		# https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication
		token = app.acquire_token_by_username_password(params["username"], params["password"], scopes=scopes)

	if "access_token" in token:
		return DDHSession(name, app, token, api_host, verify)
	else:
		raise DDHAuthenticationException(token)
