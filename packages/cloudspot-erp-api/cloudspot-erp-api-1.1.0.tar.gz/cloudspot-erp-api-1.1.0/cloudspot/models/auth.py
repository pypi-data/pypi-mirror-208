from .base import BaseModel, ObjectListModel

class AuthPermission(BaseModel):
    
    def __init__(self,
      permission=None           
    ):
        super().__init__()
        
        self.permission = permission
    
class AuthPermissions(ObjectListModel):

    def __init__(self):
        super().__init__(list=[], listObject=AuthPermission)

class AuthResponse(BaseModel):
    
    def __init__(self,
        token=None,
        company=None,
        permissions=None
    ):

        super().__init__()

        self.token = token
        self.company = company
        self.permissions = permissions if permissions else AuthPermissions()
    
class PermissionsResponse(BaseModel):
    
    def __init__(self,
        permissions=None
    ):

        super().__init__()
        
        self.permissions = permissions if permissions else AuthPermissions()

class User(BaseModel):
    
    def __init__(self,
        first_name=None,
        last_name=None,
        email=None,
        company=None,
        pin=None
    ):
        
        super().__init__()
        
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.company = company
        self.pin = pin