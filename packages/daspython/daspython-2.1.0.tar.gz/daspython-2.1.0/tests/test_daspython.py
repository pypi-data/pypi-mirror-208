import os
import unittest
import pandas as pd

from dotenv import load_dotenv
from daspython import das as das_main

class TestDasPython(unittest.TestCase):
    
    das = None
    __base_url:str
    __username:str
    __password:str
    __check_https:bool

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        load_dotenv()
        self.__base_url = str(os.getenv('DAS_URL'))
        self.__username = str(os.getenv('DAS_USERNAME'))
        self.__password = str(os.getenv('DAS_PASSWORD'))
        self.__check_https = bool(os.getenv('CHECK_HTTPS'))

    def test_get_entries(self): 

        self.das = das_main.Main(self.__base_url, self.__username, self.__password, self.__check_https)
        response = self.das.get_entries('Core')                
        unittest.TestCase.assertEqual(self, len(response.items), 10)   

    def test_download_template(self): 

        self.das = das_main.Main(self.__base_url, self.__username, self.__password, self.__check_https)
        self.das.download_template('Core', "c:\\temp\\template.xlsx")               
        unittest.TestCase.assertTrue(self, os.path.exists("c:\\temp\\template.xlsx"))

    def test_insert_data_from_excel(self):

        df = pd.read_excel('C:\\Workspace\\das-python\\core_test_template.xlsx')

        entries = []

        for index, row in df.iterrows():
            dictionary = {}
            for column in df.columns:
                dictionary[column] = row[column]
            entries.append(dictionary)

        self.das = das_main.Main(self.__base_url, self.__username, self.__password, check_https=False)            
        self.das.insert_entries(attribute_name='Core', entries=entries)                

if __name__ == '__main__':
    unittest.main()        