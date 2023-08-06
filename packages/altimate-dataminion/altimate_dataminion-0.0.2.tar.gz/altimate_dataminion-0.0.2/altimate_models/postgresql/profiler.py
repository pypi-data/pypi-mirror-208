from altimate_models.base.profiler import SQLAlchemyProfiler
from altimate_models.base.source import DataSource
from altimate_models.postgresql.dialect import PostgreSQLSourceDialect
from altimate_models.postgresql.extractor import PostgreSQLExtractor
from altimate_models.shared_models import Policy, ResourceType


class PostgreSQLProfiler(SQLAlchemyProfiler):
    def __init__(self, data_source: DataSource, policy: Policy):
        if policy.resource0.resource_type != ResourceType.TABLE:
            raise Exception("PostgreSQLProfiler only supports table resources")

        super().__init__(
            extractor=PostgreSQLExtractor(
                data_source.get_connection_string(
                    database=policy.resource0.resource.database,
                    schema=policy.resource0.resource.db_schema,
                )
            ),
            policy=policy,
            dialect=PostgreSQLSourceDialect(),
        )
