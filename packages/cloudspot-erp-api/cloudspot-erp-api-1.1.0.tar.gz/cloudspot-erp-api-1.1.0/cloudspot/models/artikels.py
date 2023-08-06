from .base import BaseModel, ObjectListModel

class ExtraInformatie(BaseModel):
    
    def __init__(self,
        text=None,
        taal=None,
        taal_display=None
    ):
        
        super().__init__()
        
        self.text = text
        self.taal = taal
        self.taal_display = taal_display    

class ExtraInformatieList(ObjectListModel):
    
    def __init__(self):
        super().__init__(list=[], listObject=ExtraInformatie)

class Prijscategorie(BaseModel):
    
    def __init__(self,
        label=None,
        label_id=None,
        type=None,
        korting=None,
        verkoopprijs_excl=None,
        verkoopprijs_incl=None           
    ):
        
        super().__init__()
        
        self.label = label
        self.label_id = label_id
        self.type = type
        self.korting = korting
        self.verkoopprijs_excl = verkoopprijs_excl
        self.verkoopprijs_incl = verkoopprijs_incl

class Prijscategorieen(ObjectListModel):
    def __init__(self):
        super().__init__(list=[], listObject=Prijscategorie)
        
class ArtikelFoto(BaseModel):
    
    def __init__(self,
        url=None,
        is_hoofdfoto=None
    ):
        super().__init__()
        
        self.url = url
        self.is_hoofdfoto = is_hoofdfoto

class ArtikelFotos(ObjectListModel):
    def __init__(self):
        super().__init__(list=[], listObject=ArtikelFoto)

class ArtikelCategorie(BaseModel):
    
    def __init__(self,
        id=None,
        naam=None,
        children=None
    ):
        
        super().__init__()
        
        self.id = id
        self.naam = naam
        self.children = children if children else ArtikelCategorieen()

class ArtikelCategorieen(ObjectListModel):
    def __init__(self):
        super().__init__(list=[], listObject=ArtikelCategorie)

class Artikel(BaseModel):
    
    def __init__(self,
        id=None,
        naam=None,
        beschrijving=None,
        interne_notitie=None,
        merk=None,
        merk_id=None,
        categorie=None,
        categorie_id=None,
        categorieen=None,
        SKU=None,
        voorraad_bijhouden=None,
        op_voorraad=None,
        product_url=None,
        verkoopprijs_excl=None,
        verkoopprijs_incl=None,
        inkoopprijs_excl=None,
        inkoopprijs_incl=None,
        bestellingtype=None,
        units_per_bestelling=None,
        BTW=None,
        status=None,
        fotos=None,
        prijscategorieen=None,
        EAN=None,
        samenstellingen=None,
        ruwe_grondstoffen=None,
        gebruiksaanwijzingen=None,
        meer_info=None,
    ):

        super().__init__()

        self.id = id
        self.naam = naam
        self.beschrijving = beschrijving
        self.interne_notitie = interne_notitie
        self.merk = merk
        self.merk_id = merk_id
        self.categorie = categorie
        self.categorie_id = categorie_id
        self.categorieen = categorieen if categorieen else ArtikelCategorieen()
        self.SKU = SKU
        self.voorraad_bijhouden = voorraad_bijhouden
        self.op_voorraad = op_voorraad
        self.product_url = product_url
        self.verkoopprijs_excl = verkoopprijs_excl
        self.verkoopprijs_incl = verkoopprijs_incl
        self.inkoopprijs_excl = inkoopprijs_excl
        self.inkoopprijs_incl = inkoopprijs_incl
        self.bestellingtype = bestellingtype
        self.units_per_bestelling = units_per_bestelling
        self.BTW = BTW
        self.status = status
        self.fotos = fotos if fotos else ArtikelFotos()
        self.prijscategorieen = prijscategorieen if prijscategorieen else Prijscategorieen()
        self.samenstellingen = samenstellingen if samenstellingen else ExtraInformatieList()
        self.ruwe_grondstoffen = ruwe_grondstoffen if ruwe_grondstoffen else ExtraInformatieList()
        self.gebruiksaanwijzingen = gebruiksaanwijzingen if gebruiksaanwijzingen else ExtraInformatieList()
        self.meer_info = meer_info if meer_info else ExtraInformatieList()
        self.EAN = EAN if EAN else []
        
class Artikels(ObjectListModel):
    def __init__(self):
        super().__init__(list=[], listObject=Artikel)
