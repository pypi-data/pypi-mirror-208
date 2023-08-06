import glob
import os
import sys
from importlib import import_module
from os.path import isfile
from typing import Callable, Iterator, Type

from dg_utilities import logging

from datagen_protocol.migrations.migration_base import MigrationBase, APIVersion

logger = logging.get_logger(__name__)

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_DATAPOINT_MIGRATIONS_PATH = os.path.join(CURRENT_DIR, "datapoint_migrations")
DEFAULT_SEQUENCE_MIGRATIONS_PATH = os.path.join(CURRENT_DIR, "sequence_migrations")


class MigrationRunner:
    @classmethod
    def apply(cls, datapoint_request: dict, migration: Type[MigrationBase]) -> None:
        logger.info(f"Applying migration to version {migration.version}")
        cls._run_migrations(datapoint_request, migration)
        cls._bump_version(datapoint_request, migration)

    @classmethod
    def _run_migrations(cls, datapoint_request: dict, migration: Type[MigrationBase]) -> None:
        for change in cls._get_schema_changes(migration):
            cls._log_change(change)
            change(datapoint_request)

    @staticmethod
    def _log_change(schema_change: Callable) -> None:
        logger.info(f"Applying migration {schema_change.__name__}")

    @staticmethod
    def _get_schema_changes(migration: Type[MigrationBase]) -> Iterator[Callable]:
        for class_attribute in dir(migration):
            if class_attribute.startswith("_schema_change"):
                yield getattr(migration, class_attribute)

    @classmethod
    def _bump_version(cls, datapoint_request: dict, migration: Type[MigrationBase]) -> None:
        datapoint_request["request_version"] = str(migration.version)

    @classmethod
    def find_migrations(cls, migrations_path: str | None) -> dict[APIVersion, Type[MigrationBase]]:
        if not migrations_path:
            migration_modules = cls._import_modules(DEFAULT_DATAPOINT_MIGRATIONS_PATH)
            migration_modules += cls._import_modules(DEFAULT_SEQUENCE_MIGRATIONS_PATH)
        else:
            migration_modules = cls._import_modules(migrations_path)
        return cls._get_migrations(migration_modules=migration_modules)

    @classmethod
    def _import_modules(cls, modules_path: str) -> list:
        sys.path.append(modules_path)
        modules = []
        for file in cls._find_python_files(modules_path):
            file_name = cls._file_name(file)
            try:
                modules.append(import_module(file_name))
            except ImportError as e:
                logger.error(f"Could not import migration {e.path}. {str(e)}")
        return modules

    @staticmethod
    def _get_migrations(migration_modules: list) -> dict[APIVersion, Type[MigrationBase]]:
        migrations = {}
        for module in migration_modules:
            try:
                migration = getattr(module, "Migration")
                migrations[migration.version] = migration
                if not issubclass(migration, MigrationBase):
                    raise TypeError("Not a proper migration module")
            except AttributeError:
                logger.error("Not a migration module")
        return migrations

    @staticmethod
    def _find_python_files(dir_path: str) -> Iterator[str]:
        for file in glob.glob(f"{dir_path}/migration_*_*.py"):
            if isfile(file):
                yield file.split("/")[-1]

    @staticmethod
    def _file_name(file: str) -> str:
        return file.split(".")[0]
