from typing import Type 
import os 
import platform

from .json_connector import JsonStoreConnector
from .store_connector import StoreConnector

class Store():
    def __init__(self, file_location: str, connector_type: Type[StoreConnector]) -> None :
        self.file_location = file_location
        self.connector:StoreConnector = None
        self._file = None
        self._connector_tpye = connector_type
    
    def _get_file_data(self):
        if self.connector: 
            return 

        dirname = os.path.dirname(self.file_location)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
        if not os.path.exists(self.file_location):
            with open(self.file_location, "w") as f:
                self.connector = self._connector_tpye(self._connector_tpye.default_value())
                return

        with open(self.file_location, "r+") as f:
            self.connector = self._connector_tpye(f.read())

    def get(self, key):
        self._get_file_data()
        return self.connector.get(key)

    def put(self, key, value):
        self._get_file_data()
        self.connector.put(key, value)
    
    def get_path(self):
        return self.file_location

    def __enter__(self):
        self._get_file_data()
        return self 

    def __exit__(self, type, value, traceback): 
        with open(self.file_location, "w") as f:
            f.write(self.connector.dump())

class CredStore(Store):
    def __init__(self) -> None:
        dir = ".pynt"
        super().__init__(file_location=os.path.join(os.path.expanduser("~"), dir, "creds.json"),
                         connector_type=JsonStoreConnector)
        
    def get_access_token(self):
        return self.get("token")["access_token"]
 
