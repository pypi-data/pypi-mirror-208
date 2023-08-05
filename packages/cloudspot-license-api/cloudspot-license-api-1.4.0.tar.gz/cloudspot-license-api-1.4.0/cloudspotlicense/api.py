import base64
import requests
import json

from cloudspotlicense.models.auth import AuthPermissions, User

from . import config
from cloudspotlicense.endpoints.auth import AuthMethods
from cloudspotlicense.constants.errors import BadCredentials, NoValidToken

class CloudspotLicense_API:

    def __init__(self, application, token=None, test_mode=False):
        self.base_url = config.TEST_URL if test_mode else config.BASE_URL
        self.headers = { 'Content-Type' : 'application/json' }
        
        self.auth = AuthMethods(self)
        self.token = token
        self.application = application
        self.user = User()
        
        self.headers.update({'X-LICENSE-MODULE' : self.application })
        self.permissions = AuthPermissions()
    
    def set_token_header(self, token):
        self.token = token
        self.headers.update({'X-LICENSE-TOKEN' : self.token})
    
    def check_header_tokens(self):
        if 'X-LICENSE-TOKEN' not in self.headers and self.token:
            self.headers.update({'X-LICENSE-TOKEN' : self.token})
        if 'X-LICENSE-MODULE' not in self.headers:
            self.headers.update({'X-LICENSE-MODULE' : self.application })
        
    def do_request(self, method, url, data=None, headers=None):
        
        if headers:
            merged_headers = self.headers.copy()
            merged_headers.update(headers)
            headers = merged_headers
        else: headers = self.headers
        
        request_url = '{base}/{url}/'.format(base=self.base_url, url=url)

        if method == 'GET':
            response = requests.get(request_url, params=data, headers=headers)
        elif method == 'POST':
            response = requests.post(request_url, data=json.dumps(data), headers=headers)
        elif method == 'PUT':
            response = requests.put(request_url, data=json.dumps(data), headers=headers)
        
        return response


    def request(self, method, url, data=None, headers=None):
        
        # Check the headers for appropriate tokens before we make a request
        self.check_header_tokens()

        # Make the request
        response = self.do_request(method, url, data, headers)
        resp_content = response.json()
        
        return response.status_code, response.headers, resp_content
    
    def get(self, url, data=None, headers=None):
        status, headers, response = self.request('GET', url, data, headers)
        return status, headers, response
    
    def post(self, url, data=None, headers=None):
        status, headers, response = self.request('POST', url, data, headers)
        return status, headers, response
    
    def put(self, url, data=None, headers=None):
        status, headers, response = self.request('PUT', url, data, headers)
        return status, headers, response
    
    def authenticate(self, username, password):
        
        auth_resp = self.auth.authenticate(username, password)
        if auth_resp.has_error: raise BadCredentials('Username or password not correct.')
        
        self.permissions = auth_resp.permissions
        self.set_token_header(auth_resp.token)

    def get_permissions(self, token=None):
        if token: self.set_token_header(token)
        perm_resp = self.auth.get_permissions()
        if perm_resp.has_error: raise NoValidToken('No valid token found.')
        
        self.permissions = perm_resp.permissions
        
    def get_user(self, token=None):
        if token: self.set_token_header(token)
        user_resp = self.auth.get_user()
        if user_resp.has_error: raise NoValidToken('No valid token found.')
        
        self.user = user_resp
    
    def get_company_permissions(self, company_id, token=None):
        if token: self.set_token_header(token)
        company_resp = self.auth.get_company_permissions(company_id)
        if company_resp.has_error: raise Exception(company_resp.error.message)
        
        return company_resp.permissions