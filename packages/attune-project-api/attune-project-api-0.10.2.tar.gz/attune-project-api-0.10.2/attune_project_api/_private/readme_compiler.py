import logging
import os
from pathlib import Path
from typing import Optional

from mako import exceptions
from mako.lookup import TemplateLookup

from attune_project_api.StorageTuple import ItemStorageGroupEnum
from attune_project_api._contexts import GitObjectStorageContext
from attune_project_api.items.parameter_tuple import niceParameterNames
from attune_project_api.items.step_tuples.step_group_tuple import StepGroupTuple


logger = logging.getLogger(__name__)


TEMPLATE_FOLDER: Path = Path(os.path.dirname(__file__) + "/templates")
ROOT_TEMPLATE = "ProjectReadme.md.mako"


class ReadmeCompiler:
    def __init__(self, context: GitObjectStorageContext):
        self._context = context

    def compile(self) -> str:
        lookup = TemplateLookup(directories=[TEMPLATE_FOLDER])
        rootTemplate = lookup.get_template(ROOT_TEMPLATE)

        blueprints = [
            s
            for s in self._context.getItems(ItemStorageGroupEnum.Step)
            if isinstance(s, StepGroupTuple) and s.isBlueprint
        ]
        files = self._context.getItems(ItemStorageGroupEnum.FileArchive)
        params = self._context.getItems(ItemStorageGroupEnum.Parameter)

        try:
            return str(
                rootTemplate.render(
                    makoGlobal={},
                    projectMetadata=self._context.metadata,
                    blueprints=blueprints,
                    files=files,
                    params=params,
                    niceParameterNames=niceParameterNames,
                    attune=None,
                )
            )
        except Exception:
            raise Exception(exceptions.text_error_template().render())
