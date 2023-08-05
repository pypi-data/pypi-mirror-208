import unittest
import sys 
sys.path.insert(0, "C:\Workspace\das-python\daspython")
import os
from dotenv import load_dotenv
from daspython.auth.authenticate import DasAuth
from daspython.common.api import Token
from daspython.services.alcs.aclservice import AclService, ChangeOwnershipRequest

class TestAclService(unittest.TestCase):

    def _get_token(self) -> Token:
        load_dotenv()
        auth = DasAuth(os.getenv("DAS_URL"), os.getenv("DAS_USERNAME"), os.getenv("DAS_PASSWORD"))
        auth.authenticate(bool(os.getenv("CHECK_HTTPS")))
        return auth

    def test_change_ownership(self):

        acl_service = AclService(self._get_token())

        payload = ChangeOwnershipRequest()
        payload.attributeId = 55
        payload.entryId = 'f3cfd83d-b95d-4876-9217-312eec681e37'
        payload.newOwnerId = 57
        
        response = acl_service.ChangeOwnership(request=payload)

        self.assertEqual(response, True)


if __name__ == '__main__':
    unittest.main()
