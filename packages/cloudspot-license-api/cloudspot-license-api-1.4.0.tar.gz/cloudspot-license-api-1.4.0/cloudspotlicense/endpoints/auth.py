from cloudspotlicense.constants.errors import NoValidToken
from .base import APIEndpoint

from cloudspotlicense.models.auth import AuthResponse, User, CompanyPermissionsResponse, ImpersonateResponse

class AuthMethods(APIEndpoint):

    def __init__(self, api):
        super().__init__(api, 'auth')
        
    def authenticate(self, username, password):
        endpoint = '{0}/{1}'.format(self.endpoint, 'authenticate')
        data = { 'username' : username, 'password' : password }
        
        status, headers, resp_json = self.api.post(endpoint, data)
        
        if status > 399: return AuthResponse().parse_error(resp_json)
        auth_resp = AuthResponse().parse(resp_json)
        
        return auth_resp
    
    def validate_impersonation(self, token):
        endpoint = '{0}/{1}'.format(self.endpoint, 'impersonation-validation')
        data = { 'token' : token }
        
        status, headers, resp_json = self.api.post(endpoint, data)
        
        if status > 399: return ImpersonateResponse().parse_error(resp_json)
        impersonate_resp = ImpersonateResponse().parse(resp_json)
        
        return impersonate_resp
    
    def get_user(self):
        if not self.api.token: raise NoValidToken('No token found. Authenticate the user first to retrieve a token or supply a token to the function.')
        
        endpoint = '{0}/{1}'.format(self.endpoint, 'users/profile')
        data = None
        
        status, headers, resp_json = self.api.get(endpoint, data)

        if status > 399: return User().parse_error(resp_json)
        user_resp = User().parse(resp_json)
        
        return user_resp
    
    def get_company_permissions(self, company_id):
        if not self.api.token: raise NoValidToken('No token found. Authenticate the user first to retrieve a token or supply a token to the function.')
        endpoint = '{0}/{1}/{2}'.format(self.endpoint, 'get-company-permissions', company_id)
        data = None
        
        status, headers, resp_json = self.api.get(endpoint, data)
        
        if status > 399: return CompanyPermissionsResponse().parse_error(resp_json)
        resp = CompanyPermissionsResponse().parse(resp_json)
        
        return resp

    def get_permissions(self):
        if not self.api.token: raise NoValidToken('No token found. Authenticate the user first to retrieve a token or supply a token to the function.')
        endpoint = '{0}/{1}'.format(self.endpoint, 'get-permissions')
        data = None
        
        status, headers, resp_json = self.api.get(endpoint, data)
        
        if status != 200: return AuthResponse().parse_error(resp_json)
        resp = AuthResponse().parse(resp_json)
        
        return resp