"""
*
 *  Copyright ServerTribe HQ Pty Ltd 2021
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  ServerTribe HQ Pty Ltd
 *
"""
from typing import List
from typing import Optional

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from . import addStepDeclarative
from .step_tuple import StepTupleTypeEnum
from ..parameter_tuple import parameterTypeCompatibleWith
from ... import ParameterTuple
from ... import StepTuple
from ...ObjectStorageContext import ObjectStorageContext
from ...RelationField import RelationField
from ...StorageTuple import ItemStorageGroupEnum
from ...StorageTuple import StorageMemberTuple


@addTupleType
class ParameterMappingTuple(StorageMemberTuple):
    """Parameter Mapping Tuple

    Mapping between a parameter in a linked project to a parameter or a literal
    text value in the linking project. At least one of `parentStaticTextValue` or
    `parentParameterKey` must be set.

    """

    __tupleType__ = "com.servertribe.attune.tuples.ParameterMappingTuple"

    # Literal value for text parameters
    parentStaticTextValue: Optional[str] = TupleField()

    # Key of the parameter or literal value in the linking project
    parentParameterKey: Optional[str] = TupleField()
    parentParameter: Optional[ParameterTuple] = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="parentParameterKey",
        cascadeOnDelete=False,
        cascadeOnUpdate=False,
    )

    # Key of the parameter in the "linked" to projects blueprint
    childProjectUuid: str = TupleField()
    childParameterUuid: str = TupleField()
    childParameterType: str = TupleField()

    # These two fields are for debugging / information purposes.
    # Do not rely on them.
    childProjectName: Optional[str] = TupleField()
    childParameterName: Optional[str] = TupleField()

    @property
    def isStaticTextSet(self) -> bool:
        return self.parentStaticTextValue is not None

    @property
    def isParentParameterSet(self) -> bool:
        return self.parentParameterKey is not None


@ObjectStorageContext.registerItemClass
@addStepDeclarative("Project Link")
@addTupleType
class StepProjectLinkTuple(StepTuple):
    __tupleType__ = StepTupleTypeEnum.PROJECT_LINK.value

    # The details of the project
    projectUuid: str = TupleField()
    cloneUrl: Optional[str] = TupleField()

    # This is either a branch name or tag name
    # In future it may support npm style tags
    projectVersion: str = TupleField()

    #: The UUID of the blueprint step
    blueprintUuid: str = TupleField()

    # These two fields are for debugging / information purposes.
    # Do not rely on them.
    projectName: Optional[str] = TupleField()
    blueprintName: Optional[str] = TupleField()

    parameterMap: List[ParameterMappingTuple] = TupleField([])

    storageParameters: list[StepTuple] = RelationField(
        ForeignClass=ParameterTuple,
        referenceKeyFieldName="parameterMap",
        isList=True,
        cascadeOnDelete=True,
        cascadeOnUpdate=True,
        memberReferenceKeyFieldName="parentParameterKey",
    )

    def parameters(self) -> list["ParameterTuple"]:
        return [
            mapping.parentParameter
            for mapping in self.parameterMap
            if mapping.isParentParameterSet
        ]

    def scriptReferences(self) -> list[str]:
        return []

    def verifyParameterMapping(
        self, targetContext: ObjectStorageContext
    ) -> list[int]:
        targetParams = set(
            [
                p.externalUuid4
                for p in targetContext.getItems(ItemStorageGroupEnum.Parameter)
            ]
        )
        invalidIndices = set()

        for i, mapping in enumerate(self.parameterMap):
            if mapping.childParameterUuid not in targetParams:
                invalidIndices.add(i)

            if (
                mapping.isParentParameterSet
                and mapping.parentParameter
                and mapping.parentParameter.type
                not in parameterTypeCompatibleWith.get(
                    mapping.childParameterType, set()
                )
            ):
                invalidIndices.add(i)

        return list(invalidIndices)
