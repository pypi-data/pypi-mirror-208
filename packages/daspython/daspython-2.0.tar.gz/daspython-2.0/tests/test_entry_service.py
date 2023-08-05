import os
from os.path import exists
import unittest
import random
from pathlib import Path
from dotenv import load_dotenv

from daspython.common.api import Token
from daspython.auth.authenticate import DasAuth
from daspython.services.searches.searchservice import SearchEntriesRequest, SearchService
from daspython.services.entries.entryservice import EntryService, GetAllEntriesRequest, GetEntryRequest, InsertRequest, UpdateRequest


class TestEntryService(unittest.TestCase):

    def _get_token(self) -> Token:
        load_dotenv()
        auth = DasAuth(os.getenv("DAS_URL"), os.getenv("DAS_USERNAME"), os.getenv("DAS_PASSWORD"))
        auth.authenticate(bool(os.getenv("CHECK_HTTPS")))
        return auth

    def test_getall(self):

        service = EntryService(self._get_token())
        request = GetAllEntriesRequest()
        request.attributeid = 55
        response = service.get_all(request)
        self.assertGreater(
            response.total, 0,  f'EntryService - Get All function should return totalCount greater than 0.')

    def test_create(self):
        service = SearchService(self._get_token())
        request = SearchEntriesRequest()
        request.attributeId = 27
        request.querystring = 'code(4.b.6rc)'
        request.maxresultcount = 1
        response = service.search_entries(request)

        event_id = response.items[0]['id']

        service = EntryService(self._get_token())
        request = InsertRequest()
        request.attributeId = 55
        request.entry = {            
            'event': event_id,
            'number': 1,
            'diameterincm': 100
        }
        new_entry_id = service.create(request)
        self.assertEqual(len(new_entry_id), 36,
                         f'EntryService - Create function should return a new valid GUID (uuid).')

    def test_update(self):
        service = SearchService(self._get_token())
        request = SearchEntriesRequest()
        request.attributeId = 55
        request.querystring = 'code(zb.b.9p)'
        request.maxresultcount = 1
        response = service.search_entries(request)

        id = response.items[0]['id']

        service = EntryService(self._get_token())
        request = UpdateRequest()
        request.attributeId = 55
        request.entry = {
            'id': id,
            'diameterincm': random.randint(1, 1000)            
        }

        response = service.update(request)
        updated_entry_id = str(response)
        self.assertEqual(
            updated_entry_id, id, f'EntryService - Update function should return {id} but returned: {updated_entry_id}')

    def test_delete(self):
        service = SearchService(self._get_token())
        request = SearchEntriesRequest()
        request.attributeId = 55
        request.querystring = 'displayname(6*)'
        request.maxresultcount = 1
        response = service.search_entries(request)

        entryId = response.items[0]['id']

        service = EntryService(self._get_token())
        response = service.delete_entry(entryId, 55)        
        self.assertEqual(response, True, f'EntryService - Delete function should return True but returned: {str(response)}')

    def test_get_entry_id(self):
        service = EntryService(self._get_token())
        result = service.get_entry_id(
            name='64PE424-20', attribute_name='Station')
        self.assertEqual(result, '4cccd80e-ab9a-4ee2-b9b2-014f07c84011',
                         f'EntryService - get_entry_id function should return 4cccd80e-ab9a-4ee2-b9b2-014f07c84011 but returned: {result}')

    def test_get_entry_by_code(self):
        service = EntryService(self._get_token())
        response = service.get_entry_by_code('h.b.znq')     
        display_name = response.entry['displayname']   
        self.assertEqual(display_name, 'C1702162.D',
                         f'EntryService - get_entry_by_code function expects:  but got {display_name}')

    def test_create_entry_from_csv_file(self):

        service = EntryService(self._get_token())

        if exists('cores2.csv'):            
            service.insert_entries_from_csv(
                csv_file='cores2.csv', attribute='Core')

    def test_save_with_csv(self):

        service = EntryService(self._get_token())
        service.create_csv_template('Core')

        self.assertEqual(Path('Core.csv').exists(
        ), True, f'EntryService - get_csv_file - A file: Core.csv should exists.')

    def test_get_entry_by_name(self):

        service = EntryService(self._get_token())
        entry = service.get_entry_by_name(
            name='SO268-16GC#02', attribute_name='Core')
        name = entry.get('displayname')
        self.assertEqual(entry.get('displayname'), 'SO268-16GC#02',
                         f'EntryService - get_entry_by_name - Expects: SO268-16GC#02 but got {name}')

    def test_create_entry_with_displaynames(self):

        service = service = EntryService(self._get_token())
        request = InsertRequest()
        request.attributeId = 24
        request.entry = {
            'Cruise': 'fa72011a-fa90-4d02-9253-d6c5d2a326e8', 
            'Number': '1234', 
            'Alias': None, 
            'Latitude (decimal)': '54.3775', 
            'Longitude (decimal)': '4.7452', 
            'Water depth in meters': '46.83', 
            'Date of arrival': '2022-06-06', 
            'Date of departure': '2022-06-06', 
            'Time of arrival': '06:06:58', 
            'Time of departure': '07:17:21'
        }

        new_entry_id = service.insert(request)
        
        self.assertEqual(len(new_entry_id), 36,
                         f'EntryService - Create function should return a new valid GUID (uuid).')  

    def test_update_entry_with_displaynames(self):

        search_service = SearchService(self._get_token())
        request = SearchEntriesRequest()
        request.attributeId = 55
        request.querystring = 'code(zb.b.y)'
        request.maxresultcount = 1
        response = search_service.search_entries(request)
        core_id = response.items[0]['id'] 

        entry_service = EntryService(self._get_token())

        new_diameter = random.randint(1, 1000)            

        edit_request = UpdateRequest()
        edit_request.attributeId = 55
        edit_request.entry = {        
            'id': core_id,
            'Number': 1,
            'Diameter': new_diameter
        } 

        entry_service.edit(edit_request)

        get_entry_request = GetEntryRequest()
        get_entry_request.id = core_id
        get_entry_request.attributeid = 55
        entry_response = entry_service.get(get_entry_request)

        self.assertEqual(entry_response['result']['entry']['diameterincm'], new_diameter,
                         f'EntryService - Create function should return a new valid GUID (uuid).')  

if __name__ == '__main__':
    unittest.main()
