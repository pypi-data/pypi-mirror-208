from altimate_models.base.extractor import SQLAlchemyExtractor
from altimate_models.base.profiler import SQLAlchemyProfiler
from altimate_models.base.source import DataSource
from altimate_models.shared_models import Policy
from altimate_models.snowflake.dialect import SnowflakeSourceDialect


class SnowflakeProfiler(SQLAlchemyProfiler):
    def __init__(self, data_source: DataSource, policy: Policy):
        super().__init__(
            extractor=SQLAlchemyExtractor(
                data_source.get_connection_string(
                    database=policy.resource0.resource.database,
                    schema=policy.resource0.resource.db_schema,
                )
            ),
            policy=policy,
            dialect=SnowflakeSourceDialect(),
        )
