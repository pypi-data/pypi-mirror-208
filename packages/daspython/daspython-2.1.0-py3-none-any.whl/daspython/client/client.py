from daspython.auth.authenticate import DasAuth
from daspython.dastypes.entry import Entry
from daspython.services.entries.entryservice import EntryService


class DasClient:

    def __init__(self, host, user, password, check_https=True) -> None:
        auth = DasAuth(host, user, password)
        auth.authenticate(check_https)
        self.__token = auth

    def get_entry(self, **kwargs) -> Entry:
        """	
        This function takes in keyword arguments (kwargs) such as code and name and returns an entry (dict) based on the provided argument(s).        
        """
        service = EntryService(self.__token)

        if 'code' in kwargs:
            response = service.get_entry_by_code(kwargs['code'])
            return response.entry
        elif 'name' in kwargs:
            response = service.get_entry_by_name(kwargs['name'])
            return response.entry
        else:
            raise ValueError('Invalid argument(s). Expected code or name.')
