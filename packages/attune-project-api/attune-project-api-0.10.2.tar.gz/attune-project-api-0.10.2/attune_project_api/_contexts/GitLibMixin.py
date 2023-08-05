import json
import logging
from abc import abstractmethod
from collections import defaultdict
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import List
from typing import Optional

import pygit2
import pytz
from pathvalidate import sanitize_filepath
from pygit2 import RemoteCallbacks

from ..Exceptions import ChangesNotCommitedError
from ..Exceptions import ItemNotFoundError
from ..Exceptions import MergeConflict
from ..Exceptions import NoChangesToCommitError
from ..Exceptions import NoRemoteDefined
from ..Exceptions import ProjectValidationError
from ..StorageTuple import ItemStorageGroupEnum
from .._private.readme_compiler import ReadmeCompiler
from ..migration import getLatestRevision
from ..tuples.git_commit_tuple import GitCommitTuple
from ..tuples.project_modified_tuple import ModifiedItemDetails
from ..tuples.project_modified_tuple import ProjectModifiedTuple


logger = logging.getLogger(__name__)

ATTUNE_WORKING_BRANCH = "__working__"

_gitignore = """
# Ignore files in directories named unversioned
**/unversioned/**
**/.DS_Store
"""


def makeRef(branch: str) -> str:
    return "refs/heads/%s" % branch


class PathNameInvalidException(Exception):
    pass


GitRemote = namedtuple("GitRemote", ["name", "url"])


class GitLibMixin:
    defaultCommitter = pygit2.Signature(
        "ServerTribe Attune", "attune@servertribe.com"
    )

    def __init__(self, projectPath: Path, projectInfo: "ContextProjectInfo"):
        self.projectPath = projectPath
        self.__committer = self.defaultCommitter
        self._repo = None
        self.__indexInitialised = False
        # TODO: What if the class was loaded before a raw commit was made?
        self.__isIndexDirty = False

        # Information required by the on-error context manager
        self._workingId: Optional[str] = None

        try:
            self.loadGitRepo()
        except pygit2.GitError:
            self.initGitRepo(projectInfo)
            self.loadGitRepo()

    @abstractmethod
    def load(self):
        pass

    @property
    def _repoPath(self) -> Path:
        return self.projectPath / "git_storage"

    @property
    def checkedOutBranchRef(self) -> str:
        return self._repo.head.raw_name

    @property
    def checkedOutBranchName(self) -> str:
        return self._repo.head.name.rsplit("/", 1)[1]

    def loadGitRepo(self):
        self._repo = pygit2.Repository(self._repoPath.as_posix())
        if self._repo.is_bare:
            raise ValueError(f"{self._repoPath} points to a Git Bare Repo")

    def initGitRepo(self, projectInfo):
        # Create target repo
        self._repo = pygit2.init_repository(self._repoPath.as_posix())
        self.__indexInitialised = True
        logger.info(f"Create Git repository at {self._repoPath}")
        self.__createInitialCommit(projectInfo)

    def __createInitialCommit(self, projectInfo):
        # We cannot use the public `writeMetadata` method here because the
        # branches and references to have not been set up yet
        self.__writeInitialProjectMetadata(projectInfo)
        self.__writeGitIgnore()
        self.__createCommit(
            "HEAD", "Create default metadata.json", [], self.__index
        )

    def __writeInitialProjectMetadata(self, projectInfo: "ContextProjectInfo"):
        # Create default metadata.json
        name = projectInfo.name
        data = json.dumps(
            {
                "revision": getLatestRevision(),
                "name": projectInfo.name,
                "key": projectInfo.key,
            },
            indent=4,
            sort_keys=True,
            separators=(", ", ": "),
        ).encode()
        path = "project/metadata.json"
        # Write the file, *without* preparing the working branch
        self.__index.add(
            pygit2.IndexEntry(
                path, self._repo.create_blob(data), pygit2.GIT_FILEMODE_BLOB
            )
        )
        self.__index.write()
        self.__isIndexDirty = True

    def __writeGitIgnore(self):
        data = _gitignore.encode()
        path = ".gitignore"
        # Write the file, with out preparing the working branch
        self.__index.add(
            pygit2.IndexEntry(
                path, self._repo.create_blob(data), pygit2.GIT_FILEMODE_BLOB
            )
        )
        self.__index.write()
        self.__isIndexDirty = True

    def writeReadme(self, content: str):
        oid = self._repo.create_blob(content.encode())
        # Ensure there is a __working__ branch present
        self.prepareWorkingBranch()
        self.__index.add(
            pygit2.IndexEntry("README.md", oid, pygit2.GIT_FILEMODE_BLOB)
        )
        self.__index.write()
        self.__isIndexDirty = True

    @classmethod
    def cloneGitRepo(
        cls,
        projectPath: Path,
        url: str,
        username: str = None,
        password: str = None,
    ):
        class RemoteCallback(RemoteCallbacks):
            def credentials(self, url, username_from_url, allowed_types):
                if username is None and password is None:
                    return super().credentials(
                        url, username_from_url, allowed_types
                    )
                elif password is None:
                    cred = pygit2.Username(username)
                else:
                    cred = pygit2.UserPass(username, password)
                return cred

            def certificate_check(self, certificate, valid, host):
                # Return whatever the TLS/SSH library thinks about the cert
                return True

        pygit2.clone_repository(
            url,
            projectPath.as_posix(),
            bare=False,
            callbacks=RemoteCallback(),
        )

    def _writeFile(self, path: str, data: bytes, mode=pygit2.GIT_FILEMODE_BLOB):
        if path != sanitize_filepath(path):
            raise PathNameInvalidException(
                "Path %s is not valid, please " "sanitize it first" % path
            )

        oid = self._repo.create_blob(data)
        self.prepareWorkingBranch()
        self.__index.add(pygit2.IndexEntry(Path(path).as_posix(), oid, mode))
        self.__index.write()
        self.__isIndexDirty = True

    def _moveDirectory(self, fromPath: Path, toPath: Path):
        if fromPath == toPath:
            raise Exception("The source and destination paths are the same")

        fromTree = self._getTree(fromPath)

        self.prepareWorkingBranch()

        def recurse(fromParentPath, toParentPath, tree):
            for item in tree:
                fromItemPath = fromParentPath / item.name
                toItemPath = toParentPath / item.name
                # A child tree is a directory
                if isinstance(item, pygit2.Tree):
                    recurse(fromItemPath, toItemPath, item)
                    continue

                # Otherwise it's a blob, move it
                assert isinstance(
                    item, pygit2.Object
                ), "item is not a pygit2.Object"
                self.__index.add(
                    pygit2.IndexEntry(
                        toItemPath.as_posix(), item.oid, item.filemode
                    )
                )
                self.__index.remove(fromItemPath.as_posix())

        recurse(fromPath, toPath, fromTree)
        self.__index.write()
        self.__isIndexDirty = True

    def _moveFile(self, fromPath: Path, toPath: Path):
        if fromPath == toPath:
            raise Exception("The source and destination paths are the same")

        fromTree = self._getTree(fromPath.parent)

        self.prepareWorkingBranch()

        blob = fromTree / fromPath.name
        assert isinstance(blob, pygit2.Object), "blob is not a pygit2.Object"

        self.__index.add(
            pygit2.IndexEntry(toPath.as_posix(), blob.oid, blob.filemode)
        )
        self.__index.remove(fromPath.as_posix())
        self.__index.write()
        self.__isIndexDirty = True

    def _deleteDirectory(self, path: Path):
        try:
            startTree = self._getTree(path)
        except FileNotFoundError:
            # It's already done.
            return

        self.prepareWorkingBranch()

        def recurse(parentPath, tree):
            for item in tree:
                itemPath = parentPath / item.name
                # A child tree is a directory
                if isinstance(item, pygit2.Tree):
                    recurse(itemPath, item)
                    continue

                # Otherwise, it's a blob, move it
                assert isinstance(
                    item, pygit2.Object
                ), "item is not a pygit2.Object"
                self.__index.remove(itemPath.as_posix())

        recurse(path, startTree)
        self.__index.write()
        self.__isIndexDirty = True

    def _deleteFile(self, path: Path):
        tree = self._getTree(path.parent)
        self.prepareWorkingBranch()

        blob = tree / path.name
        assert isinstance(blob, pygit2.Object), "blob is not a pygit2.Object"

        self.__index.remove(path.as_posix())
        self.__index.write()
        self.__isIndexDirty = True

    def _readFile(self, path: Path) -> bytes:
        try:
            fileObjectId = self.__index[str(path).strip("./").strip("/")].id
            fileObject = self._repo[fileObjectId]
            return fileObject.data

        except KeyError:
            raise FileNotFoundError()

    @property
    def isDirty(self) -> bool:
        return self.__isIndexDirty

    def commit(self, msg: str):
        descendentCommit = next(
            self._repo.walk(self.__workingBranch.target), None
        )
        if descendentCommit is not None:
            descendents = [descendentCommit.id]
        else:
            descendents = []
        self.__createCommit(
            self.__workingBranch.name, msg, descendents, self.__index
        )

    def __createCommit(
        self, targetName: str, msg: str, descendents: list[str], index
    ) -> str:
        tree = index.write_tree()
        author = self.__committer if self.__committer else self.defaultCommitter

        self.__isIndexDirty = False

        startTime = datetime.now(pytz.UTC)
        try:
            logger.debug("Committing to %s with message |%s|", targetName, msg)
            return self._repo.create_commit(
                targetName,
                author,
                author,
                msg,
                tree,
                descendents,
            )
        finally:
            logger.debug(
                "Committing to %s completed in %s",
                targetName,
                (datetime.now(pytz.UTC) - startTime),
            )

    @property
    def __index(self) -> pygit2.Index:
        if self.__indexInitialised:
            return self._repo.index

        # Else, initialise the index
        if ATTUNE_WORKING_BRANCH in list(self._repo.branches):
            self._repo.index.read_tree(
                tree=self._repo.revparse_single(
                    makeRef(ATTUNE_WORKING_BRANCH)
                ).tree
            )
        else:
            self._repo.index.read_tree(
                tree=self._repo.revparse_single(self.checkedOutBranchRef).tree
            )
        self.__indexInitialised = True

        return self._repo.index

    def prepareWorkingBranch(self):
        if ATTUNE_WORKING_BRANCH not in list(self._repo.branches):
            commit = next(self._repo.walk(self.__checkedOutBranch.target), None)
            self._repo.create_branch(ATTUNE_WORKING_BRANCH, commit)
            self.__indexInitialised = False

    @property
    def __workingBranch(self) -> pygit2.Branch:
        """Working Branch

        Accessing the working branch causes creation of __working__ branch if
        it does not already exist.

        """
        self.prepareWorkingBranch()
        return self._repo.references[makeRef(ATTUNE_WORKING_BRANCH)]

    @property
    def __checkedOutBranch(self) -> pygit2.Branch:
        return self._repo.references[self.checkedOutBranchRef]

    @property
    def __workingTree(self):
        branch = self.checkedOutBranchRef
        if ATTUNE_WORKING_BRANCH in list(self._repo.branches):
            branch = makeRef(ATTUNE_WORKING_BRANCH)

        return self._repo.revparse_single(branch).tree

    def _getTree(self, path: Path) -> pygit2.Tree:
        # We will read objects as they are at the working branch
        tree = self.__workingTree
        climbedPath = ""
        for pathComponent in path.as_posix().split("/"):
            if pathComponent == ".":
                continue
            climbedPath += f"/{pathComponent}"
            if pathComponent in tree:
                tree = tree / pathComponent
            else:
                raise FileNotFoundError(f"Path {pathComponent} does not exist")
        return tree

    def setCommitterSignature(self, name: str, email: str) -> None:
        self.__committer = pygit2.Signature(name, email)

    def allLocalBranches(self) -> List[str]:
        return [
            str(branch)
            for branch in self._repo.branches.local
            if not str(branch) == ATTUNE_WORKING_BRANCH
        ]

    def allRemoteBranches(self) -> List[str]:
        return [str(branch) for branch in self._repo.branches.remote]

    def allBranches(self) -> List[str]:
        return [str(branch) for branch in self._repo.branches]

    def allRemotes(self) -> List[GitRemote]:
        return [
            GitRemote(remote.name, remote.url) for remote in self._repo.remotes
        ]

    def checkoutBranch(self, branchName: str) -> None:
        if branchName == ATTUNE_WORKING_BRANCH:
            raise ValueError(
                "Cannot checkout the reserved Attune branch %s"
                % ATTUNE_WORKING_BRANCH
            )

        if self.isDirty:
            raise ChangesNotCommitedError()

        # Check if there are changes waiting to be squashed and merged
        if ATTUNE_WORKING_BRANCH in list(self._repo.branches):
            workingBranch = self.__workingBranch
            checkedOutBranch = self.__checkedOutBranch
            if workingBranch.target != checkedOutBranch.target:
                raise ChangesNotCommitedError()

            # Delete the working branch
            workingBranch.delete()

        if branchName in self.allLocalBranches():
            # Checkout existing branch
            self._repo.checkout(makeRef(branchName))
        else:
            # Create and checkout new branch
            checkedBranch = self.__checkedOutBranch
            commit = next(self._repo.walk(checkedBranch.target), None)
            self._repo.create_branch(branchName, commit)
            self._repo.checkout(makeRef(branchName))

    def canSquashCommit(self) -> bool:
        working = self.__workingBranch
        checkedOut = self.__checkedOutBranch

        if working.target == checkedOut.target:
            return False

        return True

    def squashAndMergeWorking(self, mergeCommitMessage: str) -> None:
        if self._workingId is not None:
            raise Exception(
                "Cannot squash and commit when modifying the working branch"
            )

        if self.isDirty:
            raise ChangesNotCommitedError(
                "There are pending changes to be committed"
            )

        if not self.canSquashCommit():
            raise NoChangesToCommitError(
                "There are no pending changes to commit"
            )

        self._generateReadme()
        # Reload the Git _repo attribute. This will drop all references held by
        # the Repository object and allow for checkout on Windows
        self.loadGitRepo()

        # Walk the commits till we find the previous common point
        checkedLastCommit = next(
            self._repo.walk(self.__checkedOutBranch.target), None
        )
        # NOTE: Do not inline this variable as self.__checkedOutBranch is a
        # dynamic property and returns the currently checked out branch which
        # could be __working__. We need a reference to the 'master' branch
        # which should be the branch checked out at this point
        checkedOutBranch = self.__checkedOutBranch

        self._repo.checkout(makeRef(ATTUNE_WORKING_BRANCH))
        # Create squash commit
        # Do a soft reset to the beginning of working branch
        self._repo.reset(checkedLastCommit.id, pygit2.GIT_RESET_SOFT)
        # Create a commit. This will squash the previous `commitsOnChecked`
        # into one

        squashCommitOid = self.__createCommit(
            makeRef(ATTUNE_WORKING_BRANCH),
            mergeCommitMessage,
            [checkedLastCommit.id],
            self.__index,
        )

        """
        Because we write files directly to the Git object database and
        never to the working directory, running a git status at this point
        will show that the files were deleted because they are not present
        in the working directory. This does not allow us to merge later as
        the repo is in a dirty state. Doing a hard reset, resets the index
        and restores the state of the working directory (in our case,
        it recreates the files that it things were deleted). This is done
        in C code and should be faster than writing files to the working
        directory in Python and then `add commit`ing them.
        """
        self._repo.reset(squashCommitOid, pygit2.GIT_RESET_HARD)

        # Reload the reference to the working branch
        working = self.__workingBranch

        self._repo.checkout(checkedOutBranch.name)
        checkedOutBranch.set_target(working.target)
        self._repo.reset(checkedOutBranch.target, pygit2.GIT_RESET_HARD)

        # Delete the working branch. It will be recreated if there is a new
        # commit
        working.delete()

    def _generateReadme(self) -> None:
        readmeCompiler = ReadmeCompiler(self)
        readmeContent = readmeCompiler.compile()
        self.writeReadme(readmeContent)
        self.commit("Updated README.md")

    @property
    def commitsOnWorkingBranchCount(self) -> int:
        if ATTUNE_WORKING_BRANCH not in self._repo.branches:
            return 0

        workingBranch = self.__workingBranch
        checkedOutBranch = self.__checkedOutBranch
        checkedLastCommit = next(self._repo.walk(checkedOutBranch.target), None)

        # Walk the commits till we find the previous common point
        commitsOnWorking = 0
        for commit in self._repo.walk(workingBranch.target):
            if commit.id == checkedLastCommit.id:
                break
            commitsOnWorking += 1

        return commitsOnWorking

    def changesSinceLastCommit(self) -> ProjectModifiedTuple:
        changes = ProjectModifiedTuple()
        changes.commitsOnWorkingBranch = self.numCommitsOnWorkingBranch()

        # Don't calculate the diff if __working__ does not exist
        if changes.commitsOnWorkingBranch == 0:
            return changes

        # The keys of this dictionary correspond to folder names in the
        # repository
        changedItems = dict(
            steps=defaultdict(lambda: None),
            parameters=defaultdict(lambda: None),
            files=defaultdict(lambda: None),
        )

        diff = self._repo.diff(
            a=self.__checkedOutBranch.target, b=self.__workingBranch.target
        )
        for delta in diff.deltas:
            change = delta.status_char()
            fileName = delta.new_file.path

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
                        name=f"<key:{itemKey}>",
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
            # Removing files such as contents/ or comment.md from an item
            # should be a modification change and not a deletion change
            # Items are only deleted when their metadata.json and folder is
            # deleted
            if (
                modifiedFile != "metadata.json"
                and newChange.changeStatus == "D"
            ):
                newChange.changeStatus = "M"
            return newChange

        # We prefer the change to the metadata.json of an item
        if modifiedFile == "metadata.json":
            return newChange

        if prevChange.changeStatus != "D" and newChange.changeStatus == "D":
            newChange.changeStatus = prevChange.changeStatus
        return newChange

    def discardWorkingBranch(self):
        if ATTUNE_WORKING_BRANCH not in self._repo.branches:
            raise Exception("There are no changes to discard")

        self._repo.branches.delete(ATTUNE_WORKING_BRANCH)
        self.load()

    def getCommits(self) -> list[GitCommitTuple]:
        for commit in self._repo.walk(self.__checkedOutBranch.target):
            gitCommit = GitCommitTuple()
            gitCommit.authorName = commit.author.name
            gitCommit.authorEmail = commit.author.email
            gitCommit.message = commit.message
            gitCommit.timestamp = datetime.fromtimestamp(
                commit.commit_time
            ).strftime("%Y-%m-%d %H:%M:%S")
            gitCommit.hash = commit.short_id

            yield gitCommit

    def addRemote(self, remote: str, url: str) -> None:
        if remote in [r[0] for r in self.allRemotes()]:
            self._repo.remotes.set_url(remote, url)
        else:
            self._repo.remotes.create(remote, url)

    def deleteRemote(self, remote: str) -> None:
        if remote in [r[0] for r in self.allRemotes()]:
            self._repo.remotes.delete(remote)
        else:
            raise ValueError(f"Remote {remote} does not exist")

    def pushToRemote(
        self, remoteName: str, username: str, password: str = None
    ) -> None:
        if remoteName not in [r[0] for r in self.allRemotes()]:
            raise NoRemoteDefined(f"Remote {remoteName} not set for project")

        logger.info("Pulling in remote changes before Pushing")
        self.pullFromRemote(remoteName, username, password)

        if not username:
            cred = None
        elif not password:
            cred = pygit2.Username(username)
        else:
            cred = pygit2.UserPass(username, password)

        remote = self._repo.remotes[remoteName]

        class RemoteCallback(RemoteCallbacks):
            def credentials(self, url, username_from_url, allowed_types):
                return cred

            def certificate_check(self, certificate, valid, host):
                # Return whatever the TLS/SSH library thinks about the cert
                return True

            def push_update_reference(self, refname, message):
                if message is not None:
                    raise Exception(
                        f"Remote rejected push with message: {message}"
                    )

        checkedOutBranch = self.__checkedOutBranch

        # The remote branch might not exist when a new repository is
        # created
        remoteBranchName = f"{remoteName}/{checkedOutBranch.shorthand}"
        if remoteBranchName in self._repo.branches:
            remoteBranch = self._repo.branches[remoteBranchName]
            if checkedOutBranch.target == remoteBranch.target:
                raise Exception("There are no commits to push")

        # TODO: This does not seem to raise any errors when a push was
        #  unsuccessful due to permission errors
        remote.push(
            [checkedOutBranch.name],
            callbacks=RemoteCallback(),
        )

    def pullFromRemote(
        self, remoteName: str, username: str, password: str = None
    ) -> None:
        if remoteName not in [r[0] for r in self.allRemotes()]:
            raise NoRemoteDefined(f"Remote {remoteName} not set for project")

        if not username:
            cred = None
        elif not password:
            cred = pygit2.Username(username)
        else:
            cred = pygit2.UserPass(username, password)

        remote = self._repo.remotes[remoteName]

        class RemoteCallback(RemoteCallbacks):
            def credentials(self, url, username_from_url, allowed_types):
                return cred

            def certificate_check(self, certificate, valid, host):
                # Return whatever the TLS/SSH library thinks about the cert
                return True

        remote.fetch(callbacks=RemoteCallback())

        checkedOutBranch = self.__checkedOutBranch
        remoteBranchName = f"{remoteName}/{checkedOutBranch.shorthand}"

        if remoteBranchName in self._repo.branches:
            # Try to merge remote equivalent into current checked out
            self.mergeBranches(remoteBranchName)

    def mergeBranches(self, sourceBranch: str) -> None:
        if sourceBranch not in self.allBranches():
            raise ValueError(f"Branch {sourceBranch} does not exist")

        checkedOutBranch = self.__checkedOutBranch
        if ATTUNE_WORKING_BRANCH in self._repo.branches:
            working = self.__workingBranch

            logger.debug(
                f"Merging branches {sourceBranch} to {checkedOutBranch.name}"
            )

            if working.target != checkedOutBranch.target:
                raise RuntimeError(
                    "There are changes pending to be committed. Please commit "
                    "them before trying again"
                )

        sourceBranchId = self._repo.branches[sourceBranch].target
        checkedBranchId = checkedOutBranch.target

        mergeAnalysis, _ = self._repo.merge_analysis(sourceBranchId)
        if mergeAnalysis & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            logger.debug("Both branches are up-to-date. Nothing to merge")
            return

        if mergeAnalysis & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            logger.debug("Branch can be fast-forwarded")
            # Fast-forward checkedOutBranch branch to source branch
            checkedOutBranch.set_target(sourceBranchId)

        elif mergeAnalysis & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
            """
            IMPORTANT!!
            The `merge` method on the `Repository` object and the merging
            procedure below is dependent on the state of the index and the
            working tree. We cannot use self.__index or any other methods
            that mutate the index or working tree here. self.__index
            reloads the index if there is no working branch which causes
            the merged index to be lost and the merged changes won't be
            committed.
            """

            logger.debug("Merging branches")
            self._repo.merge(sourceBranchId)
            # Check for merge conflicts and reverse merge if there are any
            if self._repo.index.conflicts:
                self._repo.reset(checkedBranchId, pygit2.GIT_RESET_HARD)
                raise MergeConflict("Cannot complete merge due to conflicts")

            logger.debug("Branches merged. Creating merge commit")
            self.__createCommit(
                "HEAD",
                "Merged pulled changes",
                [self._repo.head.target, sourceBranchId],
                self._repo.index,
            )

            # This is so Git CLI does not show status as MERGING
            self._repo.state_cleanup()

        else:
            raise RuntimeError("Unknown Git merge analysis result")

        checkedOutBranch = self.__checkedOutBranch
        if ATTUNE_WORKING_BRANCH in self._repo.branches:
            # Fast-forward the working branch on top of the merged branch
            # We need to reload the branch references here
            working = self.__workingBranch
            working.set_target(checkedOutBranch.target)
        # The checkedOutBranch branch status will show the modified files from the pull
        # here as staged because they were not created on disk. This will create
        # those files
        self._repo.reset(checkedOutBranch.target, pygit2.GIT_RESET_HARD)

        # Check for project validation errors after merge
        try:
            # This is the load method from GitObjectStorageContext
            self.load()
        except ProjectValidationError:
            logger.debug(
                "Merged project failed validation. Resetting to "
                "previous state"
            )
            self._repo.reset(checkedBranchId, pygit2.GIT_RESET_HARD)
            logger.debug("Project reset")
            raise Exception("Merging failed due to project validation errors")

        logger.debug("No validation errors after merge")

    def _getGitRevisionForBranch(self, name: str) -> str:
        assert name in self._repo.branches, "Branch does not exist in project"
        commit: pygit2.Commit = self._repo.revparse_single(name)
        return commit.id

    def __enter__(self):
        # Ensure that the working branch exists
        self.prepareWorkingBranch()
        self._workingId = self._getGitRevisionForBranch(ATTUNE_WORKING_BRANCH)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            # There was no error and this is a clean exit
            self._workingId = None
        else:
            logger.debug(
                f"Something went wrong. Resetting __working__ to"
                f" {self._workingId}"
            )
            checkedBranchName = self.checkedOutBranchRef
            self._repo.checkout(makeRef(ATTUNE_WORKING_BRANCH))
            self._repo.reset(self._workingId, pygit2.GIT_RESET_HARD)
            self._repo.checkout(checkedBranchName)
            self._workingId = None

            # Reset the index state so it is reinitialized
            self.__isIndexDirty = False
            self.__indexInitialised = False

            # Reload all items
            self.load()

    def diffCheckedOutToWorkingBranch(self) -> pygit2.Diff:
        return self._repo.diff(
            a=self.__checkedOutBranch.target, b=self.__workingBranch.target
        )

    def freeGitDbResources(self) -> None:
        self._repo.free()
