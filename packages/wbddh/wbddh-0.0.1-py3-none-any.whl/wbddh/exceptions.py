class DDHRequestException(Exception):
	def __init__(self, response):
		self.status_code = response.status_code
		self.text = response.text
		
	def __repr__(self):
		return f'DDH2RequestException [{self.status_code}]: {self.text}'
	
	def __str__(self):
		return self.text

class DDHSessionException(Exception):
	def __init__(self, message):
		self.message = message

	def __repr__(self):
		return f'DDHSessionException: {self.message}'
	
	def __str__(self):
		return self.message

class DDHAuthenticationException(Exception):
	def __init__(self, captured_output):
		self.error = captured_output.get("error")
		self.error_description = captured_output.get("error_description")
		self.correlation_id = captured_output.get("correlation_id")
		self.captured_output = captured_output

	def __repr__(self):
		return f'DDHAuthenticationException [{self.error}]: {self.error_description}, {self.correlation_id}'
	
	def __str__(self):
		return self.error_description
