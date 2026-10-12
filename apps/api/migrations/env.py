"""Alembic environment. Migrations are written by hand; autogenerate is only a cross-check."""

from logging.config import fileConfig

from alembic import context

import qlab.audit.models
import qlab.content.models
import qlab.rights.models
import qlab.syllabus.models  # noqa: F401
from qlab.database import Base, make_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations() -> None:
    if context.is_offline_mode():
        raise RuntimeError("offline migrations are not supported")
    # A caller (tests) may hand over its own connection; otherwise QLAB_DATABASE_URL is used.
    connection = config.attributes.get("connection")
    if connection is not None:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = make_engine(config.get_main_option("sqlalchemy.url"))
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


run_migrations()
