import os
import unittest

from dotenv import load_dotenv

from daspython.client.client import DasClient


class TestDasClient(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        load_dotenv()
        self.das_url = os.getenv('DAS_URL')
        self.das_username = os.getenv('DAS_USERNAME')
        self.das_password = os.getenv('DAS_PASSWORD')

    def test_get_entry(self):
        client = DasClient(self.das_url, self.das_username,
                           self.das_password, check_https=False)

        print(client.get_entry(code='zb.b.b8'))


if __name__ == '__main__':
    unittest.main()
