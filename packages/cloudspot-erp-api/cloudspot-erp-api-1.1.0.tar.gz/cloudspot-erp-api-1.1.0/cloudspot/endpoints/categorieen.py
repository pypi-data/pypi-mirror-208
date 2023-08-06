from .base import APIEndpoint

from cloudspot.models.artikels import ArtikelCategorieen, ArtikelCategorie

class CategorieenMethods(APIEndpoint):

    def __init__(self, api):
        super().__init__(api, 'categories')
        
    def list(self, fields=None):
        data = None
        status, headers, respJson = self.api.get(self.endpoint, data)
        
        if status != 200: return ArtikelCategorieen().parseError(respJson)
        categorieen = ArtikelCategorieen().parse(respJson['data'])
        
        return categorieen
    
    def get(self, id, fields=None):
        data = { 'id' : id }
        status, headers, respJson = self.api.get(self.endpoint, data)
        
        if status != 200: return ArtikelCategorie().parseError(respJson)
        categorie = ArtikelCategorie().parse(respJson['data'][0])
        
        return categorie