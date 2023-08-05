import json
import logging
import shutil
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable
from typing import Iterator
from typing import List
from typing import Optional

import pygit2
import pytz
from attune_project_api.items.project_metadata_tuple import ProjectMetadataTuple
from attune_project_api.items.step_tuples.step_sql_oracle_tuple import (
    StepSqlOracleTuple,
)
from attune_project_api.migration import runMigrationsForStorageContext
from twisted.internet.defer import DeferredList
from twisted.internet.defer import DeferredSemaphore
from twisted.internet.defer import inlineCallbacks
from vortex.Tuple import TUPLE_TYPES_BY_NAME
from vortex.Tuple import Tuple

from .GitLibMixin import ATTUNE_WORKING_BRANCH
from .GitLibMixin import GitLibMixin
from ..Exceptions import ItemNotFoundError
from ..Exceptions import ProjectIncorrectVersionError
from ..Exceptions import ProjectValidationError
from ..ObjectStorageContext import ObjectStorageContext
from ..ObjectStorageContext import ObjectStorageContextFileMixin
from ..ObjectStorageContext import VersionedFileContent
from ..ObjectStorageContext import VersionedFileInfo
from ..StorageTuple import ItemStorageGroupEnum
from ..StorageTuple import StorageTuple
from .._private.large_file_http_downloader import LargeFileHttpDownloader
from .._private.utils import makeStorageKey
from ..context_project_info import ContextProjectInfo
from ..items.file_archive_tuples.file_tuple_constants import (
    FileArchiveTupleTypeEnum,
)
from ..migration import checkIfLibrarySupportsRevision
from ..tuples.project_modified_tuple import ModifiedItemDetails
from ..tuples.project_modified_tuple import ProjectModifiedTuple
from ..tuples.project_modified_tuple import STAT_ADDED
from ..tuples.project_modified_tuple import STAT_DELETED
from ..tuples.project_modified_tuple import STAT_MODIFIED


logger = logging.getLogger(__name__)

DIR_CREATE_MODE = 0o700


class GitObjectStorageContextFileMixin(ObjectStorageContextFileMixin):
    CONTENTS_PATH = "contents"

    # ---------------
    # List the abstract methods we depend on

    # @abstractmethod
    # @property
    # def projectPath(self) -> Path:
    #     pass
    #
    # @abstractmethod
    # def _readFile(self, path: Path) -> bytes:
    #     pass
    #
    # @abstractmethod
    # def _writeFile(self, path: Path, data: bytes) -> None:
    #     pass
    #
    # @abstractmethod
    # def _getTree(self, path: Path) -> pygit2.Tree:
    #     pass

    # ---------------
    # Start our implementation

    @property
    def _unversionedFilesPath(self) -> Path:
        return self.projectPath / "file_storage"

    def __makeVersionedPath(self, group: ItemStorageGroupEnum, key: str):
        return Path(f"{group.value}/{makeStorageKey(key)}") / self.CONTENTS_PATH

    def readItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> bytes:
        return self._readFile(self.__makeVersionedPath(group, key) / path)

    def writeItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path, data: bytes
    ) -> None:
        self._writeFile(self.__makeVersionedPath(group, key) / path, data)

    def listItemVersionedFiles(
        self, group: ItemStorageGroupEnum, key: str
    ) -> list[VersionedFileInfo]:
        infos = []
        try:
            tree = self._getTree(self.__makeVersionedPath(group, key))
        except FileNotFoundError:
            logger.debug(
                "No content files found for Group %s, Key %s", group, key
            )
            return []

        def recurse(tree, parentPath: Path):
            for item in tree:
                if isinstance(item, pygit2.Tree):
                    recurse(item, parentPath / item.name)
                else:
                    assert isinstance(item, pygit2.Object)
                    infos.append(
                        VersionedFileInfo(
                            path=parentPath / item.name,
                            size=item.size,
                            executable=item.filemode
                            & pygit2.GIT_FILEMODE_BLOB_EXECUTABLE,
                            sha1=item.hex,
                        )
                    )

        recurse(tree, Path())
        return infos

    def hasItemVersionedFiles(
        self, group: ItemStorageGroupEnum, key: str
    ) -> bool:
        try:
            self._getTree(self.__makeVersionedPath(group, key))
            return True
        except FileNotFoundError:
            return False

    def getItemVersionedFileContent(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> Optional[VersionedFileContent]:
        try:
            tree = self._getTree(
                self.__makeVersionedPath(group, key) / path.parent
            )
        except FileNotFoundError:
            logger.error(
                "No file found for Group %s, Key %s, Path %s", group, key, path
            )
            raise

        if path.name not in tree:
            logger.error(
                "No file found for Group %s, Key %s, Path %s", group, key, path
            )
            raise FileNotFoundError()

        fileObject = tree / path.name
        if not isinstance(fileObject, pygit2.Object):
            logger.error(
                "Found a directory, not a file for Group %s, Key %s, Path %s",
                group,
                key,
                path,
            )
            raise FileNotFoundError()

        return VersionedFileContent(
            path=path,
            data=fileObject.data,
            executable=fileObject.filemode
            & pygit2.GIT_FILEMODE_BLOB_EXECUTABLE,
            sha1=fileObject.hex,
        )

    def setItemVersionedFileContent(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        path: Path,
        data: bytes,
        executable: bool,
    ) -> None:
        treePath = self.__makeVersionedPath(group, key) / path
        mode = (
            pygit2.GIT_FILEMODE_BLOB_EXECUTABLE
            if executable
            else pygit2.GIT_FILEMODE_BLOB
        )

        self._writeFile(
            treePath.as_posix(),
            data,
            mode=mode,
        )

    def moveItemVersionedFile(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        fromPath: Path,
        toPath: Path,
    ) -> None:
        fromContentPath = self.__makeVersionedPath(group, key) / fromPath
        toContentPath = self.__makeVersionedPath(group, key) / toPath
        self._moveFile(fromContentPath, toContentPath)

    def moveItemVersionedDirectory(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        fromPath: Path,
        toPath: Path,
    ) -> None:
        fromContentPath = self.__makeVersionedPath(group, key) / fromPath
        toContentPath = self.__makeVersionedPath(group, key) / toPath
        self._moveDirectory(fromContentPath, toContentPath)

    def deleteItemVersionedFile(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> None:
        contentPath = self.__makeVersionedPath(group, key) / path
        self._deleteFile(contentPath)

    def deleteItemVersionedDirectory(
        self, group: ItemStorageGroupEnum, key: str, path: Path
    ) -> None:
        contentPath = self.__makeVersionedPath(group, key) / path
        self._deleteDirectory(contentPath)

    def getItemLargeFilesPath(
        self, group: ItemStorageGroupEnum, key: str
    ) -> Path:
        path = (
            self._unversionedFilesPath
            / group.value
            / makeStorageKey(key)
            / self.CONTENTS_PATH
        )
        path.mkdir(mode=DIR_CREATE_MODE, parents=True, exist_ok=True)
        return path

    @inlineCallbacks
    def downloadLargeFiles(
        self,
        keys: List[str],
        archiveCompletedCallback: Callable[[str, int], None],
    ):
        semophore = DeferredSemaphore(4)
        deferreds = []
        archivesToBeDownloaded = []
        for key in keys:
            item = self.getItem(ItemStorageGroupEnum.FileArchive, key)

            if item.tupleType() != FileArchiveTupleTypeEnum.LARGE.value:
                continue

            path = item.archivePath
            # A large file is already present
            if path.exists():
                continue

            # Download only if item has URI to download file from
            if not item.remoteUri:
                continue

            archivesToBeDownloaded.append(item)
            downloader = LargeFileHttpDownloader(
                key, item.remoteUri, item.archivePath, archiveCompletedCallback
            )
            deferreds.append(semophore.run(downloader.download))

        deferredsResult = yield DeferredList(deferreds)
        for archive, (success, resultOrFailures) in zip(
            archivesToBeDownloaded, deferredsResult
        ):
            if success:
                logger.info(f"Downloaded large file for {archive.key}")
            else:
                logger.info(f"Failed to download file for {archive.key}")
            # TODO, Check result?


class GitObjectStorageContext(
    GitLibMixin, ObjectStorageContext, GitObjectStorageContextFileMixin
):
    def __init__(self, projectPath: Path, info: ContextProjectInfo):
        assert isinstance(projectPath, Path), "projectPath is not of type Path"
        self._projectInfo = info
        GitLibMixin.__init__(self, projectPath, info)

        """ This is equivalent to an Identity Map in SqlAlchemy Session
                Holds references to all instances fetched from the storage
                ensuring that "one and only one" reference exists for an item
                For example, s1 = getItem("Step1"), s2 = getItem("Step1")
                id(s1) == id(s2) """
        self.__instanceByKeyByGroup: dict[
            ItemStorageGroupEnum, dict[str, StorageTuple]
        ] = defaultdict(dict)

        self.__instanceByUuidByGroup: dict[
            ItemStorageGroupEnum, dict[str, StorageTuple]
        ] = defaultdict(dict)

        self.__singularInstanceGroup: dict[
            ItemStorageGroupEnum, Optional[StorageTuple]
        ] = defaultdict(lambda: None)

        self._migrateProjectMetadata(info)

    @property
    def info(self) -> ContextProjectInfo:
        return self._projectInfo

    def _migrateProjectMetadata(self, info):
        self.__singularInstanceGroup[ItemStorageGroupEnum.Project] = None

        self.__loadSingularItem(ItemStorageGroupEnum.Project, logError=False)

        revision = self.metadata.revision
        if not checkIfLibrarySupportsRevision(revision):
            raise ProjectIncorrectVersionError(
                "A newer version of Attune is "
                f"required to load the {info.name} project"
            )

        # Reload project metadata incase the migrations modified it
        self.__loadSingularItem(ItemStorageGroupEnum.Project, logError=False)

    # noinspection PyStatementEffect,PyTypeChecker
    def load(self):
        self.__instanceByKeyByGroup = defaultdict(dict)
        self.__instanceByUuidByGroup = defaultdict(dict)
        self.__singularInstanceGroup = defaultdict(lambda: None)

        # Run the migrations to bring the project to the latest revision
        # Migrations need to be run before the items are loaded and as a
        # result cannot use the public methods (getItem, addItem) in the
        # `upgrade` and `downgrade` functions
        runMigrationsForStorageContext(self)

        # Cache all items in memory upon load.
        # This will speed up the access of the data
        self.__loadItems(ItemStorageGroupEnum.Parameter)
        self.__loadItems(ItemStorageGroupEnum.FileArchive)
        self.__loadItems(ItemStorageGroupEnum.Step)

        self.__loadSingularItem(ItemStorageGroupEnum.Project)

        if self.isDirty:
            self.commit("Automatically assigned missing UUID4s")

    @property
    def metadata(self) -> ProjectMetadataTuple:
        metadata = self.__singularInstanceGroup[ItemStorageGroupEnum.Project]
        if metadata is None:
            metadata = self.__metadataLoadFallback()
        return metadata

    def __metadataLoadFallback(self):
        metadata = ProjectMetadataTuple(
            key="", name="", revision="", comment=""
        )
        try:
            metadataFile = json.loads(self._readFile(Path("metadata.json")))
        except FileNotFoundError:
            try:
                metadataFile = json.loads(
                    self._readFile(Path("project/metadata.json"))
                )
            except FileNotFoundError:
                metadataFile = {}

        if "name" in metadataFile:
            metadata.name = metadataFile["name"]
            metadata.key = makeStorageKey(metadata.name)
        else:
            metadata.name = self._projectInfo.name
            metadata.key = self._projectInfo.key

        if "revision" in metadataFile:
            metadata.revision = metadataFile["revision"]
        else:
            metadata.revision = "16e34a42a9a1"  # First revision

        return metadata

    def getItem(
        self, group: ItemStorageGroupEnum, key: str
    ) -> Optional[StorageTuple]:
        assert group in self.__instanceByKeyByGroup, (
            "Group %s is not a valid" % group
        )

        try:
            return self.__instanceByKeyByGroup[group][key]

        except KeyError:
            raise ItemNotFoundError(
                "Item not found, Group [%s], Key [%s]" % (group, key)
            )

    def getItemForExternalUuid(
        self, group: ItemStorageGroupEnum, externalUuid: str
    ) -> StorageTuple:
        assert group in self.__instanceByUuidByGroup, (
            "Group %s is not a valid" % group
        )

        try:
            return self.__instanceByUuidByGroup[group][externalUuid]

        except KeyError:
            raise ItemNotFoundError(
                "Item not found, Group [%s], UUID [%s]" % (group, externalUuid)
            )

    def getSingularItem(
        self, group: ItemStorageGroupEnum
    ) -> Optional[StorageTuple]:
        assert group in self.__singularInstanceGroup, (
            "Group %s is not a valid" % group
        )

        return self.__singularInstanceGroup[group]

    def getItems(
        self,
        group: ItemStorageGroupEnum,
    ) -> Iterator[StorageTuple]:
        assert group in self.__instanceByKeyByGroup, (
            "Group %s is not valid" % group
        )
        return iter(self.__instanceByKeyByGroup[group].values())

    def getItemMap(
        self, group: ItemStorageGroupEnum
    ) -> dict[str, StorageTuple]:
        assert group in self.__instanceByKeyByGroup, (
            "Group %s is not " "valid" % group
        )
        return self.__instanceByKeyByGroup[group].copy()

    def addItem(self, item: StorageTuple):
        item._bind(self)

        # Validate the item before storing
        self.validateItem(item)
        if item.__allowsMultiple__:
            self.validateKeyDoesNotExist(
                group=item.storageGroup, itemKey=item.key
            )

        self.__writeItem(item)
        self.__storeReferenceToTuple(item)

    def validateItem(self, item):
        # TupleField Validation
        Tuple.restfulJsonDictToTupleWithValidation(
            item.tupleToRestfulJsonDict(), item.__class__
        )
        # Tuple Validation
        for validator in self.Validators():
            validator.validate(self, item)

    def expungeItem(self, item: StorageTuple):
        # noinspection PyProtectedMember
        item._unbind()

    def expireItem(self, item: StorageTuple) -> None:
        # noinspection PyProtectedMember
        item._expire()

    def reloadItem(self, item: StorageTuple) -> StorageTuple:
        freshItem = self.__readItem(item.__class__, item.key)
        freshItem._bind(self)
        self.__storeReferenceToTuple(freshItem)
        item._expire()
        return freshItem

    def mergeItem(self, item: StorageTuple) -> StorageTuple:
        try:
            if item.__allowsMultiple__:
                existingItem = self.getItem(item.storageGroup, item.key)
            else:
                existingItem = self.getSingularItem(item.storageGroup)

            # If it's the same item we have in our store, then there is
            # nothing to do.
            if item is existingItem:
                # Rebind the item, and any member tuples it has
                item._bind(self)
                self.__writeItem(item)
                return item

        except ItemNotFoundError:
            existingItem = None

        if existingItem is None:
            raise ItemNotFoundError("Item does not yet exist in context")

        if item.tupleType() != existingItem.tupleType():
            raise TypeError("Items need to be of same type for merging")

        # Unbind the oldItem, bind the item
        self.expungeItem(existingItem)
        self.expireItem(existingItem)

        # noinspection PyProtectedMember
        item._bind(self)

        # Merge item in storage. We just need to store the item
        self.__writeItem(item)
        self.__storeReferenceToTuple(item)

        return item

    def updateItemKey(self, item: StorageTuple, newKey: str) -> None:
        if not item.storageContext:
            raise Exception(
                "Item must be merged using old key before updating to new key"
            )
        oldKey = item.key

        self.validateKeyDoesNotExist(item.storageGroup, newKey)

        # Update all the objects that reference this key
        self._cascadeUpdateKey(item, newKey)

        # Rename the item from the instance cache
        self.__removeReferenceToTuple(item)

        # Update the key
        item.key = newKey

        # Move the whole tree of contents over first, to ensure we include
        # any non-json content (EG, the versioned file archives)
        self.__moveItemDirectory(item.storageGroup, oldKey, newKey)

        # Move any unversioned storage, their storage is based on the key
        self.__moveItemUnversionedStorage(item.storageGroup, oldKey, newKey)

        # Write the updated json files, overwriting some of the files we just
        # moved
        self.__writeItem(item)

        # Store the new reference
        self.__storeReferenceToTuple(item)

    def __storeReferenceToTuple(self, item):
        assert (
            item.storageContext is self
        ), "Item must be bound before it is cached"

        if not item.__allowsMultiple__:
            self.__singularInstanceGroup[item.storageGroup] = item
            oldItem = self.__singularInstanceGroup[item.storageGroup]

        else:
            oldItem = self.__instanceByKeyByGroup[item.storageGroup].pop(
                item.key, None
            )
            if oldItem and oldItem.externalUuid4:
                self.__instanceByUuidByGroup[item.storageGroup].pop(
                    item.externalUuid4, None
                )

        # If we have an old UUID, **ALWAYS** keep that.
        if (
            oldItem
            and oldItem.externalUuid4
            and oldItem.externalUuid4 != item.externalUuid4
        ):
            item.externalUuid4 = oldItem.externalUuid4
            logger.debug(
                "Assigning UUID4 %s from old %s with key %s",
                item.externalUuid4,
                item.storageGroup.value,
                item.key,
            )

        elif not item.externalUuid4:
            item.externalUuid4 = str(uuid.uuid4())
            logger.debug(
                "Assigning UUID4 %s to %s with key %s",
                item.externalUuid4,
                item.storageGroup.value,
                item.key,
            )

            self.__writeItem(item, metadataOnly=True)

        if not item.__allowsMultiple__:
            self.__singularInstanceGroup[item.storageGroup] = item

        else:
            if (
                item.externalUuid4
                in self.__instanceByUuidByGroup[item.storageGroup]
            ):
                raise Exception(
                    f"Duplicate UUID4 {item.externalUuid4} "
                    f"detected in {item.storageGroup.value}"
                )

            self.__instanceByKeyByGroup[item.storageGroup][item.key] = item
            self.__instanceByUuidByGroup[item.storageGroup][
                item.externalUuid4
            ] = item

    def __removeReferenceToTuple(self, item):
        if item.__allowsMultiple__:
            self.__instanceByKeyByGroup[item.storageGroup].pop(item.key, None)
            self.__instanceByUuidByGroup[item.storageGroup].pop(
                item.externalUuid4, None
            )
        else:
            self.__singularInstanceGroup.pop(item.storageGroup)

    def __loadItems(self, group: ItemStorageGroupEnum) -> None:
        # noinspection PyStatementEffect
        self.__instanceByKeyByGroup[group]
        # noinspection PyStatementEffect
        self.__instanceByUuidByGroup[group]

        startTime = datetime.now(pytz.utc)
        try:
            tree = self._getTree(Path(group.value))
        except FileNotFoundError:
            return

        BaseClass = GitObjectStorageContext._BaseClassByGroup[group]
        assert BaseClass.__allowsMultiple__, (
            f"Items of {group.value} " f"contain a single instance"
        )

        errors = []
        for object_tree in tree:
            # object_tree.name is the sanitized key (i.e. folder name) and not
            # the name of the tuple
            try:
                item = self.__readItem(BaseClass, object_tree.name)
            except (TypeError, ItemNotFoundError) as e:
                errors.append(
                    "Group %s, Key %s, Error: %s"
                    % (group.value, object_tree.name, str(e))
                )
                continue

            item._bind(self)
            self.__storeReferenceToTuple(item)

        if errors:
            for error in errors:
                logger.info(f"Project load error: {error}")
            raise ProjectValidationError(errors)

        logger.debug(
            "Completed loading group %s in %s",
            group,
            datetime.now(pytz.utc) - startTime,
        )

    def __loadSingularItem(
        self, group: ItemStorageGroupEnum, logError=True
    ) -> None:
        # noinspection PyStatementEffect
        self.__singularInstanceGroup[group]

        try:
            tree = self._getTree(Path(group.value))
        except FileNotFoundError:
            return None

        BaseClass = GitObjectStorageContext._BaseClassByGroup[group]
        assert not BaseClass.__allowsMultiple__, (
            f"Items of {group.value} " f"contain multiple instances"
        )

        try:
            item = self.__readItem(BaseClass)
        except Exception as e:
            if logError:
                logger.exception(e)
                logger.debug(f"Error in loading group {group.value}: {str(e)}")
            return None

        item._bind(self)
        self.__storeReferenceToTuple(item)

    def __writeItem(self, item: type[StorageTuple], metadataOnly=False) -> None:
        fields = item.tupleToRestfulJsonDict()
        comment = fields.pop("comment", None)
        # Scripts and SQL is stored under a `script.txt` file
        script = fields.pop("script", None) or fields.pop("sql", None)

        itemPath = self.__makeItemPath(item)

        self._writeFile(
            (itemPath / "metadata.json").as_posix(),
            json.dumps(
                fields,
                indent=4,
                sort_keys=True,
                separators=(", ", ": "),
            ).encode(),
        )

        if metadataOnly:
            return

        if comment:
            self._writeFile(
                (itemPath / "README.md").as_posix(), comment.encode()
            )
        else:
            try:
                self._deleteFile(itemPath / "README.md")
            except (
                KeyError,
                OSError,
            ):
                # Saving an item where the comment did not exist
                pass

        if script:
            self._writeFile(
                (itemPath / "script.txt").as_posix(), script.encode()
            )

    def __makeItemPath(self, item):
        if item.key != makeStorageKey(item.key):
            logger.warning(
                "item key is invalid, it must be the result of "
                "makeStorageKey(item.key), Expected %s, got %s",
                makeStorageKey(item.key),
                item.key,
            )

        if not item.__allowsMultiple__:
            itemPath = Path(f"{item.storageGroup.value}")
        else:
            itemPath = Path(f"{item.storageGroup.value}/{item.key}")
        return itemPath

    def __moveItemDirectory(
        self, group: ItemStorageGroupEnum, oldKey: str, newKey: str
    ):
        oldKeyPath = Path(f"{group.value}/{oldKey}")
        newKeyPath = Path(f"{group.value}/{newKey}")
        self._moveDirectory(oldKeyPath, newKeyPath)

    def __moveItemUnversionedStorage(
        self,
        group: ItemStorageGroupEnum,
        key: str,
        newKey: str,
    ) -> None:
        oldPath = self.getItemLargeFilesPath(group, key)
        newPath = self.getItemLargeFilesPath(group, newKey)

        if oldPath.exists():
            newPath.parent.mkdir(
                mode=DIR_CREATE_MODE, parents=True, exist_ok=True
            )
            if newPath.exists():
                shutil.rmtree(newPath)

            shutil.move(oldPath, newPath.parent)

            if oldPath.parent.exists():
                shutil.rmtree(oldPath.parent)

    def __deleteItem(self, item: type[StorageTuple]) -> None:
        group = item.storageGroup.value
        itemPath = Path(f"{group}/{item.key}")
        self._deleteDirectory(itemPath)

    def __readItem(
        self, ItemClass: type[StorageTuple], key: str = None
    ) -> StorageTuple:
        groupStr = ItemClass.storageGroup.value
        if ItemClass.__allowsMultiple__:
            assert key, f"Expected a key for reading item {groupStr}"
            path = Path(f"{groupStr}/{makeStorageKey(key)}")
        else:
            if key:
                logger.debug(
                    f"Unexpected key {key} to readItem for group {groupStr}"
                )
            path = Path(f"{groupStr}")

        try:
            data = self._readFile(path / "metadata.json")
            metadataStr = data.decode()
            metadata = json.loads(metadataStr)
        except FileNotFoundError:
            raise ItemNotFoundError(f"{key} does not exist in {groupStr}")

        try:
            commentData = self._readFile(path / "README.md")
            metadata["comment"] = commentData.decode()
        except FileNotFoundError:
            metadata["comment"] = None  # Most tuples default this anyway

        # Check for a script, only if out step type has one
        if "type" in metadata:
            ConcreteItemClass = TUPLE_TYPES_BY_NAME[metadata["type"]]
            if hasattr(ConcreteItemClass, "script") or hasattr(
                ConcreteItemClass, "sql"
            ):
                try:
                    scriptData = self._readFile(path / "script.txt")
                    # Not every item has target 'script' or `sql` associated with it
                    if scriptData is not None:
                        metadata[
                            "sql"
                            if metadata["type"]
                            == StepSqlOracleTuple.tupleType()
                            else "script"
                        ] = scriptData.decode()
                except FileNotFoundError:
                    pass

        # noinspection PyTypeChecker
        return Tuple.restfulJsonDictToTupleWithValidation(metadata, ItemClass)

    def deleteItem(self, item: StorageTuple):
        if item.storageContext is None:
            raise ValueError(f"ObjectStorageContext not bound to {item.name}")

        self.__deleteItem(item)

        self.__removeReferenceToTuple(item)
        self.expungeItem(item)
        self.expireItem(item)
        self._cascadeDelete(item)

    def discardChangesSincePrevCommit(self):
        if ATTUNE_WORKING_BRANCH not in self._repo.branches:
            raise Exception("There are no changes to discard")

        self._repo.branches.delete(ATTUNE_WORKING_BRANCH)
        self.load()

    def renameProject(self, newName: str):
        """
        The user should not be able to rename when there is a __working__
        branch present. This is because we want the user to be able to revert
        and discard the changes on the __working__ branch. If rename is
        reverted, the Attune DB and the project name committed to
        `metadata.json` in the project will be out-of-sync
        """
        if ATTUNE_WORKING_BRANCH in self._repo.branches:
            raise RuntimeError(
                "There are changes pending to be committed. Please commit "
                "them before trying again"
            )

        metadata = self.metadata
        metadata.name = newName
        metadata.key = makeStorageKey(newName)

        self.mergeItem(metadata)
        self.commit("Write metadata with new name")
        self.squashAndMergeWorking(f"Renamed project to {newName}")

    @property
    def changesSinceLastCommit(self) -> ProjectModifiedTuple:
        changes = ProjectModifiedTuple()
        changes.commitsOnWorkingBranch = self.commitsOnWorkingBranchCount

        # Don't calculate the diff if __working__ does not have any commits
        if changes.commitsOnWorkingBranch == 0:
            return changes

        # The keys of this dictionary correspond to folder names in the
        # repository
        changedItems = dict(
            steps=defaultdict(lambda: None),
            parameters=defaultdict(lambda: None),
            files=defaultdict(lambda: None),
        )

        diff = self.diffCheckedOutToWorkingBranch()
        for delta in diff.deltas:
            change = delta.status_char()
            fileName = delta.new_file.path

            if "/" not in fileName:  # Ignore changes to files in root directory
                logger.info(f"Ignoring file {fileName} from changelog")
                continue

            itemType, itemKey, *pathTail = fileName.split("/")
            # We only include item modifications for now
            # TODO: Expand this to include other changes
            if itemType not in changedItems:
                continue

            modifiedFile = pathTail[-1]

            if itemType == "steps":
                itemGroup = ItemStorageGroupEnum.Step
            elif itemType == "parameters":
                itemGroup = ItemStorageGroupEnum.Parameter
            elif itemType == "files":
                itemGroup = ItemStorageGroupEnum.FileArchive
            else:
                raise NotImplementedError()

            try:
                item = self.getItem(itemGroup, itemKey)
            except ItemNotFoundError:
                changedItems[itemType][itemKey] = self._mergeItemChange(
                    changedItems[itemType][itemKey],
                    ModifiedItemDetails(
                        key=itemKey,
                        name=f"{{key:{itemKey}}}",
                        changeStatus=change,
                    ),
                    modifiedFile,
                )
                continue
            changedItems[itemType][itemKey] = self._mergeItemChange(
                changedItems[itemType][itemKey],
                ModifiedItemDetails(
                    key=itemKey,
                    name=item.name,
                    changeStatus=change,
                ),
                modifiedFile,
            )

        changes.modifiedSteps = list(changedItems["steps"].values())
        changes.modifiedFiles = list(changedItems["files"].values())
        changes.modifiedParams = list(changedItems["parameters"].values())

        return changes

    def _mergeItemChange(
        self,
        prevChange: ModifiedItemDetails,
        newChange: ModifiedItemDetails,
        modifiedFile: str,
    ) -> ModifiedItemDetails:
        if prevChange is None:
            # Removing/Adding files such as contents/ or comment.md from an item
            # should be a modification change and not a deletion/add change
            # Items are only deleted/added when their metadata.json and
            # folder is deleted/added
            if modifiedFile != "metadata.json" and newChange.changeStatus in (
                STAT_DELETED,
                STAT_ADDED,
            ):
                newChange.changeStatus = STAT_MODIFIED
            return newChange

        # We prefer the change to the metadata.json of an item
        if modifiedFile == "metadata.json":
            return newChange

        if (
            prevChange.changeStatus != STAT_DELETED
            and newChange.changeStatus in (STAT_DELETED, STAT_ADDED)
        ):
            newChange.changeStatus = prevChange.changeStatus
        return newChange
