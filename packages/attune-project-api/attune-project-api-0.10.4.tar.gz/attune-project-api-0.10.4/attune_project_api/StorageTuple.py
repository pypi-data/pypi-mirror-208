import logging
import weakref
from abc import ABCMeta
from collections import namedtuple
from enum import Enum
from typing import Optional

import markdown

# Hide the import and loaded messages
logging.getLogger("MARKDOWN").setLevel(logging.INFO)

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField

from attune_project_api.items import NotZeroLenStr

StorageItemKeyTuple = namedtuple(
    "StorageItemKeyTuple", ["projectKey", "itemKey"]
)


class ItemStorageGroupEnum(Enum):
    Step = "steps"
    Parameter = "parameters"
    FileArchive = "files"

    Project = "project"


class StorageMemberTuple(Tuple):
    """Storage Member Tuple

    A storage member tuple is a tuple that is a member of a storage tuple.
     For example.

         class DotTuple(StorageMemberTuple):
             pass

         class Thing2Tuple(StorageTuple):
             myMember:list[DotTuple] = TupleField()

    StorageMemberTuples are required as they store the main parent, not
    the context.

    StorageMemberTuples can have relations.

    For now, StorageMemberFields can only be one level deep off a StorageTuple

    """

    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)
        self.__parentWeakRef = None

    @property
    def storageParent(self) -> Optional["StorageTuple"]:
        return self.__parentWeakRef() if self.__parentWeakRef else None


class StorageTuple(Tuple, metaclass=ABCMeta):
    __group__: ItemStorageGroupEnum = None
    __allowsMultiple__: bool = True

    __EXPIRED__ = "expired"

    #: Keys are used for internal references between objects in this project
    # This is done to keep the project readable.
    key: NotZeroLenStr = TupleField(None, jsonExclude=False)

    #: UUIDs should be referenced by systems external to this project.
    # It should be like this because renames are hard to track in
    # disconnected systems.
    # This UUID will be assigned by this python package if it's missing
    externalUuid4: Optional[str] = TupleField()

    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)
        self.__ctx = None

    @classmethod
    def niceName(cls) -> str:
        return cls.__name__

    def _bind(self, ctx: "ObjectStorageContext") -> None:
        if self.__ctx is self.__EXPIRED__:
            raise Exception("This tuple is expired and cannot be bound")
        self.__ctx = ctx

        # Tell our member tuples that we're their parent StorageTuple
        for member in [getattr(self, f) for f in self.tupleFieldNames()]:
            # Handle lists and not lists
            if not isinstance(member, list):
                member = [member]
            for listItem in member:
                if isinstance(listItem, StorageMemberTuple):
                    listItem._StorageMemberTuple__parentWeakRef = weakref.ref(
                        self
                    )

    def _unbind(self) -> None:
        self.__ctx = None

    def _expire(self):
        self.__ctx = self.__EXPIRED__

    @property
    def storageIsExpired(self) -> bool:
        return self.__ctx == self.__EXPIRED__

    @property
    def storageContext(self) -> "ObjectStorageContext":
        return self.__ctx

    @property
    def storageProject(self) -> "ContextProjectInfo":
        return self.__ctx.info

    @property
    def storageKeyTuple(self) -> StorageItemKeyTuple:
        return StorageItemKeyTuple(self.storageProject.key, self.key)

    @classmethod
    @property
    def storageGroup(cls) -> ItemStorageGroupEnum:
        return cls.__group__

    def makeCommentHtml(self, topHeaderNum: int = 1) -> str:
        return markdown.markdown(
            self.makeCommentMarkdown(topHeaderNum=topHeaderNum),
            extensions=[
                "markdown.extensions.tables",
                "markdown.extensions.fenced_code",
                "markdown.extensions.sane_lists",
            ],
        )

    def makeCommentMarkdown(self, topHeaderNum: int = 1) -> str:
        assert hasattr(
            self, "comment"
        ), "This storage tuple has no comment field"

        if not self.comment:
            return ""

        leastHeader = 6
        for h in range(6, 0, -1):
            if ("#" * h + " ") in self.comment:
                leastHeader = h
                break

        # If highest header is <
        headerDelta = topHeaderNum - leastHeader
        if headerDelta == 0:
            return self.comment

        # This makes the first heading on line 0 of the text match the
        # pattern. We then strip the final result of this whitespace
        comment = f"\n{self.comment}"
        for h in range(6, 0, -1):
            comment = comment.replace(
                "\n%s " % ("#" * h), "\n%s " % ("#" * (h + headerDelta))
            )

        return comment.lstrip()

    @property
    def hasErrors(self) -> bool:
        return False
