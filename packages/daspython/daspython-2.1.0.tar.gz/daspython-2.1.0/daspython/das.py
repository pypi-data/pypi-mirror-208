from daspython.auth.authenticate import DasAuth
from daspython.services.attributes.attributeservice import AttributeService
from daspython.services.entries.entryservice import EntryService, GetAllEntriesRequest, InsertRequest
from daspython.common.api import Token
from daspython.services.entryfields.entryfieldservice import DisplayType

class Main():

    __token: Token

    def __init__(self, base_url:str, username:str, password:str, check_https:bool=True):
        auth = DasAuth(base_url, username, password)
        auth.authenticate(check_https)
        self.__token = auth

    def get_entries(self, attribute_name, page = 0, max_results_per_page = 10, sort = "displayname asc", filter = ""):

        service = EntryService(self.__token)
        request = GetAllEntriesRequest()

        attribute_service = AttributeService(self.__token)
        attribute_id = attribute_service.get_attribute_id(attribute_name)

        request.skipcount = page
        request.maxresultcount = max_results_per_page
        request.sorting = sort
        request.querystring = filter
        request.attributeid = attribute_id        

        return service.get_all(request)
    
    def insert_entries(self, attribute_name, entries):

        service = service = EntryService(self.__token)
        request = InsertRequest()

        attribute_service = AttributeService(self.__token)
        attribute_id = attribute_service.get_attribute_id(attribute_name)        
        request.attributeId = attribute_id
        service.insert_from_excel(attribute_id, entries)
    
    def download_template(self, attriubte_name, file_path):

        service = AttributeService(self.__token)
        attribute_service = AttributeService(self.__token)
        attribute_id = attribute_service.get_attribute_id(attriubte_name)
        service.get_file_template(attribute_id, 1, file_path)   

        
