from .base import BaseModel, ObjectListModel

class ImpersonateResponse(BaseModel):
    
    def __init__(self,
        token=None,
        auth_token=None,
        user=None,
        company=None
    ):
        super().__init__()
        
        self.token = token
        self.auth_token = auth_token
        self.user = user
        self.company = company

class AuthPermission(BaseModel):
    
    def __init__(self,
        company_id=None,
        company_name=None,
        permissions=None           
    ):
        super().__init__()
        
        self.company_id = company_id
        self.company_name = company_name
        self.permissions = permissions
    
class AuthPermissions(ObjectListModel):

    def __init__(self):
        super().__init__(list=[], listObject=AuthPermission)

class AuthResponse(BaseModel):
    
    def __init__(self,
        token=None,
        permissions=None
    ):

        super().__init__()

        self.token = token
        self.permissions = permissions if permissions else AuthPermissions()

class User(BaseModel):
    
    def __init__(self,
        first_name=None,
        last_name=None,
        email=None,
        pin=None
    ):
        
        super().__init__()
        
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.pin = pin

class CompanyPermissionsResponse(BaseModel):
    def __init__(self,
        permissions=None
    ):

        super().__init__()
        
        self.permissions = permissions