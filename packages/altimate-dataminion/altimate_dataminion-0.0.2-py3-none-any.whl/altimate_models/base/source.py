from typing import Dict, Optional, Text

from pydantic.main import BaseModel


class DataSource(BaseModel):
    id: Optional[Text]
    name: Text
    type: Text
    description: Optional[Text]
    connection_info: Optional[Text]
    connection_hash: Optional[Text]

    @classmethod
    def prompt(cls, data_store_config: Dict):
        raise NotImplementedError()

    def cred_prompt(self):
        raise NotImplementedError()

    @classmethod
    def get_connection_information(cls, data_store_config: Dict):
        raise NotImplementedError()

    def test_connection(self):
        raise NotImplementedError()

    def get_connection_string(self, *args, **kwargs) -> Text:
        raise NotImplementedError

    def drop_credentials(self):
        raise NotImplementedError

    def get_resource(self):
        raise NotImplementedError

    def get_identifier_and_fqn(self):
        raise NotImplementedError

    @classmethod
    def get_resource_config(cls, resource_config: Dict):
        raise NotImplementedError()

    @classmethod
    def map_config_to_source(cls, config: Dict):
        raise NotImplementedError()

    @classmethod
    def get_config_from_url(cls, connection_info: str):
        raise NotImplementedError()

    def update_credentials(self, key: str):
        raise NotImplementedError()
    
    def override_schema(self, schema):
        raise NotImplementedError()

    def get_dict(self):
        config = self.dict()
        config.pop("connection_hash")
        config.pop("connection_info")
        return config
