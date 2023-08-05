"""Rename comment.md to README.md for items

Revision ID: 145c6dc54454
Revises: ba6a8e4d7e2b
Create Date: 2023-02-10 10:31:31.243625

"""
from pathlib import Path

from attune_project_api.StorageTuple import ItemStorageGroupEnum


# revision identifiers, used by Alembic.
revision = "145c6dc54454"
down_revision = "ba6a8e4d7e2b"
branch_labels = None
depends_on = None


def upgrade(storageContext):
    itemGroups = [
        ItemStorageGroupEnum.Step,
        ItemStorageGroupEnum.Parameter,
        ItemStorageGroupEnum.FileArchive,
    ]

    changesMade = False

    for group in itemGroups:
        try:
            tree = storageContext._getTree(Path(group.value))
        except FileNotFoundError:
            continue

        for object_tree in tree:
            if "comment.md" in object_tree:
                itemPath = Path(group.value) / Path(object_tree.name)
                storageContext._moveFile(
                    itemPath / "comment.md",
                    itemPath / "README.md",
                )
                changesMade = True

    if changesMade:
        storageContext.commit("Move */comment.md to */README.md")


def downgrade():
    pass
