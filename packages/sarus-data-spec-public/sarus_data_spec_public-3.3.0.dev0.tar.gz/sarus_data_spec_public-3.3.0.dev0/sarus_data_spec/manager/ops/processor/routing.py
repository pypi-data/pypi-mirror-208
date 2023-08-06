import logging
import typing as t

import pyarrow as pa

from sarus_data_spec.manager.ops.base import (
    DatasetImplementation,
    DatasetStaticChecker,
    DataspecStaticChecker,
    ScalarImplementation,
)
from sarus_data_spec.manager.ops.processor.external.external_op import (  # noqa: E501
    ExternalDatasetOp,
    ExternalDatasetStaticChecker,
    ExternalScalarOp,
    ExternalScalarStaticChecker,
)

try:
    from sarus_data_spec.manager.ops.processor.standard.differentiated_sample import (  # noqa: E501
        DifferentiatedSample,
        DifferentiatedSampleStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: DifferentiatedSampling not available.")

from sarus_data_spec.manager.ops.processor.standard.extract import (
    Extract,
    ExtractStaticChecker,
)
from sarus_data_spec.manager.ops.processor.standard.filter import (
    Filter,
    FilterStaticChecker,
)
from sarus_data_spec.manager.ops.processor.standard.get_item import (
    GetItem,
    GetItemStaticChecker,
)
from sarus_data_spec.manager.ops.processor.standard.project import (
    Project,
    ProjectStaticChecker,
)

try:
    from sarus_data_spec.manager.ops.processor.standard.sample import (
        Sample,
        SampleStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: Sample not available.")

from sarus_data_spec.manager.ops.processor.standard.select_sql import (
    SelectSQL,
    SelectSQLStaticChecker,
)
from sarus_data_spec.manager.ops.processor.standard.shuffle import (
    Shuffle,
    ShuffleStaticChecker,
)

try:
    from sarus_data_spec.manager.ops.processor.standard.protection_utils.protected_paths import (  # noqa: E501
        ProtectedPaths,
        ProtectedPathsStaticChecker,
        PublicPaths,
        PublicPathStaticChecker,
    )
    from sarus_data_spec.manager.ops.processor.standard.protection_utils.protection import (  # noqa: E501
        ProtectedDataset,
        ProtectedDatasetStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: Protection not available.")

try:
    from sarus_data_spec.manager.ops.processor.standard.user_settings.automatic import (  # noqa: E501
        AutomaticUserSettings,
        AutomaticUserSettingsStaticChecker,
    )
    from sarus_data_spec.manager.ops.processor.standard.user_settings.user_settings import (  # noqa: E501
        UserSettingsDataset,
        UserSettingsStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: UserSettings not available.")
try:
    from sarus_data_spec.manager.ops.processor.standard.assign_budget import (  # noqa: E501
        AssignBudget,
        AssignBudgetStaticChecker,
    )
    from sarus_data_spec.manager.ops.processor.standard.budgets_ops import (  # noqa: E501
        AttributesBudget,
        AttributesBudgetStaticChecker,
        AutomaticBudget,
        AutomaticBudgetStaticChecker,
        SDBudget,
        SDBudgetStaticChecker,
    )

except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: Transforms with budgets not available.")
try:
    from sarus_data_spec.manager.ops.processor.standard.synthetic import (  # noqa: E501
        SamplingRatios,
        SamplingRatiosStaticChecker,
        Synthetic,
        SyntheticStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: Synthetic not available.")

try:
    from sarus_data_spec.manager.ops.processor.standard.derive_seed import (  # noqa: E501
        DeriveSeed,
        DeriveSeedStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: Seed transforms not available.")
try:
    from sarus_data_spec.manager.ops.processor.standard.group_by_pe import (  # noqa: E501
        GroupByPE,
        GroupByPEStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: GroupPE not available.")
try:
    from sarus_data_spec.manager.ops.processor.standard.transcode import (  # noqa: E501
        Transcode,
        TranscodeStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: GroupPE not available.")
try:
    from sarus_data_spec.manager.ops.processor.standard.user_settings.relationship_spec import (  # noqa: E501
        RelationshipSpecOp,
        RelationshipSpecOpStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: RelationshipSpec not available.")
try:
    from sarus_data_spec.manager.ops.processor.standard.user_settings.validated import (  # noqa: E501
        ValidatedUserTypeOp,
        ValidatedUserTypeOpStaticChecker,
    )
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("Transforms: ValidatedUserType not available.")
import sarus_data_spec.typing as st


def get_dataset_op(
    transform: st.Transform,
) -> t.Tuple[t.Type[DatasetImplementation], t.Type[DatasetStaticChecker]]:
    if transform.is_external():
        return ExternalDatasetOp, ExternalDatasetStaticChecker
    elif transform.protobuf().spec.HasField('sample'):
        return Sample, SampleStaticChecker
    elif transform.protobuf().spec.HasField('differentiated_sample'):
        return DifferentiatedSample, DifferentiatedSampleStaticChecker
    elif transform.protobuf().spec.HasField('protect_dataset'):
        return ProtectedDataset, ProtectedDatasetStaticChecker
    elif transform.protobuf().spec.HasField('user_settings'):
        return UserSettingsDataset, UserSettingsStaticChecker
    elif transform.protobuf().spec.HasField('filter'):
        return Filter, FilterStaticChecker
    elif transform.protobuf().spec.HasField('project'):
        return Project, ProjectStaticChecker
    elif transform.protobuf().spec.HasField('shuffle'):
        return Shuffle, ShuffleStaticChecker
    elif transform.protobuf().spec.HasField('synthetic'):
        return Synthetic, SyntheticStaticChecker
    elif transform.protobuf().spec.HasField('get_item'):
        return GetItem, GetItemStaticChecker
    elif transform.protobuf().spec.HasField('assign_budget'):
        return AssignBudget, AssignBudgetStaticChecker
    elif transform.protobuf().spec.HasField('group_by_pe'):
        return GroupByPE, GroupByPEStaticChecker
    elif transform.name() == 'Transcode':
        return Transcode, TranscodeStaticChecker
    elif transform.protobuf().spec.HasField('select_sql'):
        return SelectSQL, SelectSQLStaticChecker
    elif transform.protobuf().spec.HasField('extract'):
        return Extract, ExtractStaticChecker
    else:
        raise NotImplementedError(
            f"{transform.protobuf().spec.WhichOneof('spec')}"
        )


def get_scalar_op(
    transform: st.Transform,
) -> t.Tuple[t.Type[ScalarImplementation], t.Type[DataspecStaticChecker]]:
    if transform.is_external():
        return ExternalScalarOp, ExternalScalarStaticChecker
    elif transform.name() == 'automatic_protected_paths':
        # here we assume this transform is called
        # on a single dataset
        return ProtectedPaths, ProtectedPathsStaticChecker
    elif transform.name() == 'automatic_public_paths':
        # here we assume this transform is called
        # on a single dataset
        return PublicPaths, PublicPathStaticChecker
    elif transform.name() == 'automatic_user_settings':
        return AutomaticUserSettings, AutomaticUserSettingsStaticChecker
    elif transform.name() == 'automatic_budget':
        return AutomaticBudget, AutomaticBudgetStaticChecker
    elif transform.name() == 'attributes_budget':
        return AttributesBudget, AttributesBudgetStaticChecker
    elif transform.name() == 'sd_budget':
        return SDBudget, SDBudgetStaticChecker
    elif transform.name() == 'sampling_ratios':
        return SamplingRatios, SamplingRatiosStaticChecker
    elif transform.name() == 'derive_seed':
        return DeriveSeed, DeriveSeedStaticChecker
    elif transform.name() == 'relationship_spec':
        return RelationshipSpecOp, RelationshipSpecOpStaticChecker
    elif transform.name() == 'validated_user_type':
        return ValidatedUserTypeOp, ValidatedUserTypeOpStaticChecker
    else:
        raise NotImplementedError(f"scalar_transformed for {transform}")


class TransformedDataset(DatasetImplementation):
    def __init__(self, dataset: st.Dataset):
        super().__init__(dataset)
        transform = self.dataset.transform()
        ImplementationClass, StaticCheckerClass = get_dataset_op(transform)
        self.implementation = ImplementationClass(dataset)
        self.static_checker = StaticCheckerClass(dataset)

    async def private_queries(self) -> t.List[st.PrivateQuery]:
        return await self.static_checker.private_queries()

    async def to_arrow(
        self, batch_size: int
    ) -> t.AsyncIterator[pa.RecordBatch]:
        return await self.implementation.to_arrow(batch_size)

    async def schema(self) -> st.Schema:
        return await self.static_checker.schema()

    async def size(self) -> st.Size:
        return await self.implementation.size()

    async def multiplicity(self) -> st.Multiplicity:
        return await self.implementation.multiplicity()

    async def bounds(self) -> st.Bounds:
        return await self.implementation.bounds()

    async def marginals(self) -> st.Marginals:
        return await self.implementation.marginals()

    async def sql(
        self,
        query: t.Union[str, t.Mapping[t.Union[str, t.Tuple[str, ...]], str]],
        dialect: t.Optional[st.SQLDialect] = None,
        batch_size: int = 10000,
    ) -> t.AsyncIterator[pa.RecordBatch]:
        return await self.implementation.sql(query, dialect, batch_size)


class TransformedScalar(ScalarImplementation):
    def __init__(self, scalar: st.Scalar):
        super().__init__(scalar)
        transform = self.scalar.transform()
        ImplementationClass, StaticCheckerClass = get_scalar_op(transform)
        self.implementation = ImplementationClass(scalar)
        self.static_checker = StaticCheckerClass(scalar)

    async def value(self) -> t.Any:
        return await self.implementation.value()

    async def private_queries(self) -> t.List[st.PrivateQuery]:
        return await self.static_checker.private_queries()
