"""Store name in project metadata

Revision ID: 0aa489aa66b2
Revises: 58b1656aac40
Create Date: 2022-06-27 13:56:12.316172

"""
import json
from pathlib import Path

# revision identifiers, used by Alembic.
from attune_project_api import ObjectStorageContext
from attune_project_api._contexts import GitObjectStorageContext
from attune_project_api._private.utils import makeStorageKey

revision = "0aa489aa66b2"
down_revision = "58b1656aac40"
branch_labels = None
depends_on = None

PATH = Path("metadata.json")


def upgrade(storageContext: GitObjectStorageContext):
    try:
        readme = json.loads(storageContext._readFile(PATH).decode())
    except FileNotFoundError:
        readme = {}

    projectInfo = storageContext._projectInfo

    readme["name"] = projectInfo.name
    readme["key"] = makeStorageKey(projectInfo.name)
    storageContext._writeFile(
        Path(PATH).as_posix(),
        json.dumps(
            readme,
            indent=4,
            sort_keys=True,
            separators=(", ", ": "),
        ).encode(),
    )
    storageContext.commit("Store project name in metadata.json")


def downgrade(storageContext: ObjectStorageContext):
    pass
