from .base import APIEndpoint

from cloudspot.models.artikels import Artikels, Artikel

class ArtikelMethods(APIEndpoint):

    def __init__(self, api):
        super().__init__(api, 'artikels')
        
    def list(self, fields=None):
        data = None
        status, headers, respJson = self.api.get(self.endpoint, data)
        
        if status != 200: return Artikels().parseError(respJson)
        artikels = Artikels().parse(respJson['data'])
        
        return artikels
    
    def get(self, id, fields=None):
        data = { 'id' : id }
        status, headers, respJson = self.api.get(self.endpoint, data)
        
        if status != 200: return Artikels().parseError(respJson)
        artikel = Artikel().parse(respJson['data'][0])
        
        return artikel