import logging
import os

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from attune_project_api import ObjectStorageContext
from attune_project_api.StorageTuple import ItemStorageGroupEnum


logger = logging.getLogger(__name__)


def runMigrationsForStorageContext(storageContext: ObjectStorageContext):
    currentRev = storageContext.metadata.revision

    # Create a temporary database file and an engine to it
    engine = create_engine("sqlite:///")
    # Load the alembic_version table and insert the project value into it
    engine.execute("CREATE TABLE alembic_version(version_num varchar)")
    engine.execute(
        f"INSERT INTO alembic_version (version_num) VALUES ('{currentRev}')"
    )
    # We don't seem to need a commit

    # Load the migration scripts and
    codeDir = os.path.dirname(os.path.realpath(__file__))
    configFilePath = os.path.join(codeDir, "alembic.ini")
    migrationsDir = os.path.join(codeDir, "alembic_migrations")

    config = Config(file_=configFilePath)
    config.set_main_option("script_location", migrationsDir)
    script = ScriptDirectory.from_config(config)
    latestRev = script.get_heads()[0]

    # The migration context expects a function to return an iterator of
    # revisions from a current revision (`revision`) to the destination
    # revision `latestRev`. The `script._upgrade_revs` method provides such
    # an iterator built from the scripts under `versions`
    def migrations_fn(revision, _ctx):
        return script._upgrade_revs(latestRev, revision)

    with engine.connect() as conn:
        context = MigrationContext.configure(
            connection=conn,
            opts={"transactional_ddl": False, "fn": migrations_fn},
        )

        if currentRev != latestRev:
            logger.info("Running migrations for Project API")
            with storageContext:
                context.run_migrations(storageContext=storageContext)

                metadata = storageContext.metadata
                metadata.revision = latestRev
                if storageContext.getSingularItem(ItemStorageGroupEnum.Project):
                    storageContext.mergeItem(metadata)
                else:
                    storageContext.addItem(metadata)
                storageContext.commit("Update revision to latest")

            storageContext.squashAndMergeWorking(
                f"Migrate to {latestRev} revision"
            )


def getLatestRevision() -> str:
    codeDir = os.path.dirname(os.path.realpath(__file__))
    configFilePath = os.path.join(codeDir, "alembic.ini")
    migrationsDir = os.path.join(codeDir, "alembic_migrations")

    config = Config(file_=configFilePath)
    config.set_main_option("script_location", migrationsDir)
    script = ScriptDirectory.from_config(config)
    # We expect attune-project-api to never have branches in the migration
    # scripts, and it should be safe to assume there is only one head
    return script.get_heads()[0]


def checkIfLibrarySupportsRevision(revision: str) -> bool:
    """
    Check if this version of attune-project-api supports the revision read
    from a project. Projects can only be loaded if the project revision is
    smaller than the highest supported version.

    :param revision: Revision of project to load
    :return: True if project can be loaded else False
    """
    codeDir = os.path.dirname(os.path.realpath(__file__))
    configFilePath = os.path.join(codeDir, "alembic.ini")
    migrationsDir = os.path.join(codeDir, "alembic_migrations")

    config = Config(file_=configFilePath)
    config.set_main_option("script_location", migrationsDir)
    script = ScriptDirectory.from_config(config)

    # We expect attune-project-api to never have branches in the migration
    # scripts, and it should be safe to use "head" as the head
    supportedRevisions = [
        s.revision for s in script.walk_revisions(base="base", head="head")
    ]
    return revision in supportedRevisions
