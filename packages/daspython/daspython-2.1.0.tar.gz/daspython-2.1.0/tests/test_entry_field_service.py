import os
import unittest
from dotenv import load_dotenv
from daspython.common.api import Token
from daspython.auth.authenticate import DasAuth
from daspython.services.entryfields.entryfieldservice import EntryFieldService, DisplayType


class TestEntryService(unittest.TestCase):
    def _get_token(self) -> Token:
        load_dotenv()
        auth = DasAuth(os.getenv("DAS_URL"), os.getenv("DAS_USERNAME"), os.getenv("DAS_PASSWORD"))
        auth.authenticate(bool(os.getenv("CHECK_HTTPS")))
        return auth

    def test_getall(self):

       service = EntryFieldService(self._get_token())       
       response = service.get_all(55, DisplayType.FORM)
       self.assertGreater(response.total, 0, f'EntryFieldService - Get All function should return totalCount greater than 0.')


if __name__ == '__main__':
    unittest.main()
