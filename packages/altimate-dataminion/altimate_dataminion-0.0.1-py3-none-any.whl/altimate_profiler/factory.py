from typing import Text

from altimate_models.base.extractor import SQLAlchemyExtractor
from altimate_models.base.metadata_profiler import SqlAlchemyMetadataProfiler
from altimate_models.base.source import DataSource
from altimate_models.postgresql.dialect import PostgreSQLSourceDialect
from altimate_models.postgresql.profiler import PostgreSQLProfiler

# from altimate_profiler.duckdb_profiler.dialect import DuckDBSourceDialect
# from altimate_profiler.duckdb_profiler.extractor import DuckDBExtractor
# from altimate_profiler.duckdb_profiler.files.csv.dialect import CsvSourceDialect
# from altimate_profiler.duckdb_profiler.files.json.dialect import JsonSourceDialect
# from altimate_profiler.duckdb_profiler.files.parquet.dialect import ParquetSourceDialect
# from altimate_profiler.duckdb_profiler.metadata.profiler import DuckDBMetadataProfiler
# from altimate_profiler.duckdb_profiler.source.s3.models import S3Profiler
# from altimate_profiler.duckdb_profiler.transformer.schema_transformer import DuckDBSchemaTransformer
from altimate_models.shared_models import Policy
from altimate_models.snowflake.dialect import SnowflakeSourceDialect
from altimate_models.snowflake.profiler import SnowflakeProfiler
from altimate_profiler.exceptions import AltimateDataStoreNotSupported
from altimate_profiler.transformer.base import Transformer
from altimate_profiler.transformer.schema import SchemaTransformer


class SchemaTransformerFactory:
    SOURCE_MAP = {
        "snowflake": SchemaTransformer,
        "postgres": SchemaTransformer,
        # "s3": DuckDBSchemaTransformer,
    }
    TABLE_SOURCES = ["snowflake", "postgres"]
    FILE_SOURCES = ["s3"]

    @classmethod
    def create(cls, data_source_type: Text) -> Transformer:
        transformer = cls.SOURCE_MAP.get(data_source_type)
        if transformer is None:
            raise AltimateDataStoreNotSupported("Invalid data store type")
        return transformer


class MetadataFactory:
    DATA_SOURCE_TO_PROFILER = {
        "snowflake": SqlAlchemyMetadataProfiler,
        "postgres": SqlAlchemyMetadataProfiler,
        # "s3": DuckDBMetadataProfiler,
    }

    @classmethod
    def create(
        cls,
        data_source: DataSource,
        policy: Policy,
        resource_name: Text,
    ):
        profiler = cls.DATA_SOURCE_TO_PROFILER.get(data_source.type)
        dialect = DialectFactory.create(data_source)
        if not profiler:
            raise AltimateDataStoreNotSupported("Data source is not supported!")

        return profiler(data_source, dialect, policy, resource_name)


class ProfilerFactory:
    DATA_SOURCE_TO_PROFILER = {
        "snowflake": SnowflakeProfiler,
        "postgres": PostgreSQLProfiler,
        # "s3": S3Profiler,
    }

    @classmethod
    def create(cls, data_source: DataSource, policy: Policy):
        profiler = cls.DATA_SOURCE_TO_PROFILER.get(data_source.type)
        if not profiler:
            raise AltimateDataStoreNotSupported("Data source is not supported!")

        return profiler(data_source, policy)


class DialectFactory:
    DATA_SOURCE_TO_DIALECT = {
        "snowflake": SnowflakeSourceDialect,
        "postgres": PostgreSQLSourceDialect,
        # "s3": {
        #     "csv": CsvSourceDialect,
        #     "parquet": ParquetSourceDialect,
        #     "json": JsonSourceDialect,
        # }
    }

    @classmethod
    def create(cls, data_source: DataSource):
        if data_source.type == "s3":
            dialect = cls.DATA_SOURCE_TO_DIALECT.get(data_source.type).get(
                data_source.file_format
            )
        else:
            dialect = cls.DATA_SOURCE_TO_DIALECT.get(data_source.type)

        if not dialect:
            raise AltimateDataStoreNotSupported("Data source is not supported!")
        return dialect


class ExtractorFactory:
    DATA_SOURCE_TO_Extractor = {
        "snowflake": SQLAlchemyExtractor,
        "postgres": SQLAlchemyExtractor,
        # "s3": DuckDBExtractor,
    }

    @classmethod
    def create(cls, data_source: DataSource):
        extractor = cls.DATA_SOURCE_TO_Extractor.get(data_source.type)
        if not extractor:
            raise AltimateDataStoreNotSupported("Data source is not supported!")
        return extractor
