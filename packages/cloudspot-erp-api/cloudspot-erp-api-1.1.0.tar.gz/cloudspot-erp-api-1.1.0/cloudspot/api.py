import base64
import requests
import json

from warnings import warn

from cloudspot.models.auth import AuthPermissions, User

from . import config
from .authhandler import AuthHandler
from cloudspot.endpoints.auth import AuthMethods
from cloudspot.endpoints.artikels import ArtikelMethods
from cloudspot.endpoints.klanten import KlantenMethods
from cloudspot.endpoints.categorieen import CategorieenMethods
from cloudspot.constants.errors import BadCredentials, NoValidToken

class CloudspotERP_API:

    def __init__(self, test_mode=False):
        self.base_url = config.TEST_URL if test_mode else config.BASE_URL
        self.headers = { 'Content-Type' : 'application/json' }
        self.authhandler = AuthHandler()
        
        self.auth = AuthMethods(self)
    
    def set_token_header(self, token):
        self.token = token
        self.headers.update({'X-ERP-TOKEN' : self.token})
    
    def check_header_tokens(self):
        pass

    def do_request(self, method, url, data=None, headers=None):
        
        if headers:
            merged_headers = self.headers.copy()
            merged_headers.update(headers)
            headers = merged_headers
        else: headers = self.headers

        reqUrl = '{base}/{url}/'.format(base=self.base_url, url=url)

        if method == 'GET':
            response = requests.get(reqUrl, params=data, headers=headers)
        elif method == 'POST':
            response = requests.post(reqUrl, data=json.dumps(data), headers=headers)
        elif method == 'PUT':
            response = requests.put(reqUrl, data=json.dumps(data), headers=headers)
        
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


class CloudspotERP_CompanyAPI(CloudspotERP_API):
    
    def __init__(self, token, test_mode=False):
        super().__init__(test_mode=test_mode)
        self.token = token
        
        self.artikels = ArtikelMethods(self)
        self.categorieen = CategorieenMethods(self)
        self.klanten = KlantenMethods(self)
    
    def check_header_tokens(self):
        if 'X-ERP-TOKEN' not in self.headers:
            self.headers.update({'X-ERP-TOKEN' : self.token})
    

class CloudspotERP_UserAPI(CloudspotERP_API):
    
    def __init_subclass__(cls, **kwargs):
        """This throws a deprecation warning on subclassing."""
        raise DeprecationWarning(f'{cls.__name__} is deprecated. Please use the Cloudspot License wrapper.')

    def __init__(self, requestor, token=None, test_mode=False):
        raise DeprecationWarning(f'{self.__class__.__name__} is deprecated. Please use the Cloudspot License wrapper.')
        if token: self.set_token_header(token)
        user_resp = self.auth.get_user()
        if user_resp.hasError: raise NoValidToken('No valid token found.')
        
        self.user = user_resp