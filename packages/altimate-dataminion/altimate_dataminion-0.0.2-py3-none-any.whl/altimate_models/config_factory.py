from enum import Enum
from typing import Dict

from altimate_models.base.source import DataSource
from altimate_models.postgresql.source import PostgresSource
from altimate_models.s3.source import S3Source
from altimate_models.snowflake.source import SnowflakeSource


class DataStoreType(Enum):
    SNOWFLAKE = "snowflake"
    POSTGRES = "postgres"
    S3 = "s3"


class DataStoreConfigFactory:
    CLASSES = {
        DataStoreType.SNOWFLAKE: SnowflakeSource,
        DataStoreType.POSTGRES: PostgresSource,
        DataStoreType.S3: S3Source,
    }

    @classmethod
    def prompt(cls, data_store_config: Dict) -> DataSource:
        return cls.CLASSES[DataStoreType(data_store_config["type"])].prompt(
            data_store_config
        )

    @classmethod
    def create(cls, data_store_config: Dict) -> DataSource:
        data_store_config = cls.CLASSES[
            DataStoreType(data_store_config["type"])
        ].map_config_to_source(data_store_config)
        return cls.CLASSES[DataStoreType(data_store_config["type"])](
            **data_store_config
        )

    @classmethod
    def create_from_connection_string(cls,type: str, name:str, connection_string: str, key: str) -> DataSource:
        class_obj: DataSource = cls.CLASSES[DataStoreType(type)]
        configs = class_obj.get_config_from_url(
            connection_string
        )
        configs["name"] = name
        configs["type"] = type
        return_obj: DataSource = class_obj(**configs)
        return_obj.update_credentials(key)
        return return_obj