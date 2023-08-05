from sqlalchemy import create_engine

from altimate_models.base.extractor import SQLAlchemyExtractor


class PostgreSQLExtractor(SQLAlchemyExtractor):
    def _initialize(self):
        if self.engine and self.connection:
            return

        try:
            self.engine = create_engine(self.connection_str)
            self.connection = self.engine.connect()
            self.connection.execution_options(
                postgresql_readonly=True,
            )
        except Exception:
            raise
