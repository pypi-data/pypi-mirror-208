"""Move metadata.json file to project/metadata.json

Revision ID: ba6a8e4d7e2b
Revises: 0aa489aa66b2
Create Date: 2023-01-27 08:42:09.294469

"""
import json
from pathlib import Path

from attune_project_api._contexts import GitObjectStorageContext
from attune_project_api._private.utils import makeStorageKey


# revision identifiers, used by Alembic.
revision = "ba6a8e4d7e2b"
down_revision = "0aa489aa66b2"

OLD_PATH = Path("metadata.json")
NEW_PATH = Path("project/metadata.json")


def upgrade(storageContext: GitObjectStorageContext):
    # Store the key in the project metadata.json
    readme = json.loads(storageContext._readFile(OLD_PATH).decode())
    readme["key"] = makeStorageKey(readme["name"])
    storageContext._writeFile(
        Path(OLD_PATH).as_posix(),
        json.dumps(
            readme,
            indent=4,
            sort_keys=True,
            separators=(", ", ": "),
        ).encode(),
    )
    storageContext.commit("Add key to metadata.json file")

    # Move the metadata.json to new path
    storageContext._moveFile(OLD_PATH, NEW_PATH)
    storageContext.commit("Move metadata.json to project/metadata.json")


def downgrade(storageContext: GitObjectStorageContext):
    storageContext._moveFile(NEW_PATH, OLD_PATH)
    storageContext.commit("Move metadata.json to project/metadata.json")
