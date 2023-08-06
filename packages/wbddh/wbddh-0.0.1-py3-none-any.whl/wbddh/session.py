import os
import sys
import msal
from datetime import datetime, timedelta
import logging
import pickle
import json
from .utils import *
from .exceptions import *

session_instance = None

class DDHSession():
	def __init__(self, app, token, resource, cache=False, verify=None, default_refresh='auto'):
		self.azToken = token
		self.cache = cache
		self.verify = verify
		self.default_refresh = default_refresh
		self.application = app
		self.scope = token['scope']
		self.host = resource
		self.host = self.host.replace('qa', 'uat')
		self.headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
		self.expiresOn = token['expiresOn'] #datetime.strptime(token['expiresOn'], '%Y-%m-%d %H:%M:%S.%f')

		if cache:
			cache_session(self)

	def __repr__(self):
		return 'DDH2Session(resource="{}", userid="{}", expires="{}", cache={})'.format(self.host,
																						self.azToken['userId'],
																						self.azToken['expiresOn'],
																						self.cache)

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
			refresh = self.default_refresh

		if refresh == 'never' or (refresh == 'auto' and (datetime.now() + timedelta(seconds=3)) < self.expiresOn):
			return

		logging.info('access_token has expired; requesting a new one')
		accounts = self.application.get_accounts()
		chosen = None
		if accounts:
			logging.info("Account(s) exists in cache, probably with token too. Let's try.")
			print("Pick the account you want to use to proceed:")
			for a in accounts:
				print(a["username"])
			# Assuming the end user chose this one
			chosen = accounts[0]
			# Now let's try to find a token in cache for this account
		ts = datetime.now()
		new_token = self.application.acquire_token_silent(self.scope, account=chosen)
#		context = adal.AuthenticationContext(self.azToken['_authority'], api_version=None)
#		new_token = context.acquire_token_with_refresh_token(self.azToken['refreshToken'], self.azToken['_clientId'],
#															 self.azToken['resource'])

		self.azToken.update(new_token)
		self.headers['Authorization'] = 'Bearer {}'.format(new_token['access_token'])
		self.expiresOn = ts + timedelta(seconds=new_token['expires_in'])

#		self.expiresOn = datetime.strptime(new_token['expiresOn'], '%Y-%m-%d %H:%M:%S.%f')
		if self.cache:
			cache_session(self)



def create_session(name='adal_service_account_session', params=None, cache=False, autoCopy=True, verify=None):
	defaults = {'authorityHostUrl': 'https://login.microsoftonline.com',
		'resource': '00000002-0000-0000-c000-000000000000',
		'tenant': None,
		'clientId': None,
		'scope': []}

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
		if not params[key] and key != 'scope':
			raise ValueError('{} must be a defined config parameter'.format(key))

	authority_url = '/'.join([params['authorityHostUrl'], params['tenant']])
	app = msal.PublicClientApplication(
		params["clientId"], authority=authority_url,
		# token_cache=...  # Default cache is in memory only.
						   # You can learn how to use SerializableTokenCache from
						   # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
		)

	# The pattern to acquire a token looks like this.
	result = None

	accounts = app.get_accounts()
	if accounts:
		logging.info("Account(s) exists in cache, probably with token too. Let's try.")
		print("Pick the account you want to use to proceed:")
		for a in accounts:
			print(a["username"])
		# Assuming the end user chose this one
		chosen = accounts[0]
		# Now let's try to find a token in cache for this account
		result = app.acquire_token_silent(params["scope"], account=chosen)

	if not result:
		logging.info("No suitable token exists in cache. Let's get a new one from AAD.")

		flow = app.initiate_device_flow(scopes=params["scope"])
		if "user_code" not in flow:
			raise ValueError(
				"Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

		print(flow["message"])
		sys.stdout.flush()  # Some terminal needs this to ensure the message is shown

		# Ideally you should wait here, in order to save some unnecessary polling
		# input("Press Enter after signing in from another device to proceed, CTRL+C to abort.")

		token = app.acquire_token_by_device_flow(flow)  # By default it will block
		return DDHSession(app, token, cache, verify)






def create_service_account_session_msal(name='default_service_account_session', params=None, cache=False, verify=None):
	import msal
	defaults = {
		'resource': None,
		'authority': 'https://login.microsoftonline.com',
		'clientId': None,
		'username': None,
		'password': None,
		'scope': None
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
		if not params[key] and key != 'scope':
			raise ValueError('{} must be a defined config parameter'.format(key))

	app = msal.PublicClientApplication(
		params["clientId"], authority=params["authority"],
		# token_cache=...  # Default cache is in memory only.
		# You can learn how to use SerializableTokenCache from
		# https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
	)
	result = None

	# Firstly, check the cache to see if this end user has signed in before
	accounts = app.get_accounts(username=params["username"])
	ts = datetime.now()
	if accounts:
		logging.info("Account(s) exists in cache, probably with token too. Let's try.")
		result = app.acquire_token_silent(params["scope"], account=accounts[0])

	if not result:
		logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
		# See this page for constraints of Username Password Flow.
		# https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication

		# get timestamp first so can have expiry_on before token expires
		result = app.acquire_token_by_username_password(
			params["username"], params["password"], scopes=[])  # params["scope"])

	if "access_token" in result:
		token = result #['access_token']
		token['expiresOn'] = ts + timedelta(seconds=token['expires_in'])
	else:
		print(result.get("error"))
		print(result.get("error_description"))
		print(result.get("correlation_id"))  # You may need this when reporting a bug

	return DDH2Session(app, token, params['resource'], cache, verify)





def cache_session_path(name='default_session', params=None, cache=False, autoCopy=True, verify=None):

	return os.path.join(os.path.expanduser('~'), 'ddh2ext-saved-session.pkl')

def cache_session(session):
	'''Save a ddh session to a file on disk to restore later

	Arguments:
		token:	token to save

	Returns:
		None
	'''

	with open(cache_session_path(), 'wb') as fd:
		pickle.dump(session.azToken, fd)





def resume_session(verify=None):
	'''Try to resume a previously cached session. The resumed session is also treated as cached,
	and you should only have one cached session in operation at a time.

	Arguments:
		verify:		Passed to requests to specify SSL certificates, or False to disable

	Returns:
		A DDH2Session object if the session can be resumed, else None
	'''


	path = cache_session_path()
	if os.path.isfile(path):
		with open(path, 'rb') as fd:
			token = pickle.load(fd)
			session = DDHSession(token, False, verify)
			session.cache = True

			# this may return an expired session that can't be refreshed; that's normally what we want
			return session

