from pathlib import Path

import yaml
from yaml.loader import SafeLoader

class YAMLFile():
    """
    YAMLFile is base class that is used to read and write YAML files
    """
    def __init__(self, path: Path):
        super().__init__()
        self._path = path

    @property
    def path(self) -> Path:
        return self._path
    
    def exists(self) -> bool:
        return self._path.exists()
    
    def read(self) -> dict:
        with open(self._path, 'r') as stream:
            return yaml.load(stream, Loader=SafeLoader)
        
    def __str__(self) -> str:
        return self._path.as_posix()
    

class PureMLConfigYML():
    """
    PureMLConfigYML is a class that is used to generate the configuration file `puremlconfig.yaml`
    It is capable of reading and writing the configuration file
    """
    def __init__(self, path: Path):
        self._yaml_file = YAMLFile(path)
        self._yaml_document = None 

    @property
    def file(self) -> YAMLFile:
        return self._yaml_file
    
    @property
    def data(self) -> dict:
        if self._yaml_document is None:
            if self._yaml_file.exists():
                self._yaml_document = self._yaml_file.read()
            else:
                self._yaml_document = {}
        return self._yaml_document
    
    def save(self, data: dict = None) -> None:
        if data is None:
            data = self.data
        if len(data.keys()) == 0:
            print("No configuration data to save")
            return
        with open(self._yaml_file.path, 'w') as stream:
            yaml.dump(data, stream, default_flow_style=False)
    
    def reload(self) -> None:
        self._yaml_document = None