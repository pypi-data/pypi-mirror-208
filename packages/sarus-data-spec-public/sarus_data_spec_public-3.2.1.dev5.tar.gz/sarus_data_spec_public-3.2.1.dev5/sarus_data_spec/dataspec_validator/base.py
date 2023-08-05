from __future__ import annotations

from typing import Collection, List, Optional, cast
import json
import logging

from sarus_data_spec.attribute import attach_properties
from sarus_data_spec.constants import (
    IS_PUBLIC,
    NO_TOKEN,
    PEP_TOKEN,
    PRIVATE_QUERY,
)
from sarus_data_spec.dataspec_validator.privacy_limit import DeltaEpsilonLimit
from sarus_data_spec.manager.async_utils import sync
from sarus_data_spec.manager.ops.processor import routing
from sarus_data_spec.protobuf.utilities import dejson
from sarus_data_spec.protobuf.utilities import json as proto_to_json
from sarus_data_spec.storage.typing import Storage
from sarus_data_spec.variant_constraint import (
    pep_constraint,
    public_constraint,
    syn_constraint,
)
import sarus_data_spec.dataspec_validator.simple_rules as verification_rules
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

try:
    from sarus_differential_privacy.protobuf.private_query_pb2 import (
        PrivateQuery as ProtoPrivateQuery,
    )
    from sarus_differential_privacy.query import BasePrivateQuery

except ImportError:
    # Warning raised in typing.py
    pass

logger = logging.getLogger(__name__)


class BaseDataspecValidator:
    def __init__(self, storage: Storage):
        self._storage = storage

    def storage(self) -> Storage:
        return self._storage

    def verified_constraints(
        self, dataspec: st.DataSpec
    ) -> List[st.VariantConstraint]:
        """Return the list of VariantConstraints attached to a DataSpec.

        A VariantConstraint attached to a DataSpec means that the DataSpec
        verifies the constraint.
        """
        constraints = self.storage().referring(
            dataspec, type_name=sp.type_name(sp.VariantConstraint)
        )
        return cast(List[st.VariantConstraint], list(constraints))

    def verifies(
        self,
        variant_constraint: st.VariantConstraint,
        kind: st.ConstraintKind,
        public_context: Collection[str],
        privacy_limit: Optional[st.PrivacyLimit],
    ) -> bool:
        """Check if the constraint attached to a Dataspec meets requirements.

        This function is useful because comparisons are not straightforwards.
        For instance, a Dataspec might have the variant constraint SYNTHETIC
        attached to it. This synthetic dataspec also verifies the DP constraint
        and the PUBLIC constraint.

        Args:
            variant_constraint: VariantConstraint attached to the Dataspec
            kind: constraint kind to verify compliance with
            public_context: actual current public context
            epsilon: current privacy consumed
        """
        return verification_rules.verifies(
            variant_constraint=variant_constraint,
            kind=kind,
            public_context=public_context,
            privacy_limit=privacy_limit,
        )

    def is_dp(self, dataspec: st.DataSpec) -> bool:
        """Return True if the dataspec is the result of a DP transform.

        This is a simple implementation. This function checks if the
        dataspec's transform has a privacy budget and a random seed as an
        argument.
        """
        if not dataspec.is_transformed():
            return False

        parents, kwparents = dataspec.parents()
        parents = list(parents) + list(kwparents.values())
        scalars = [
            cast(st.Scalar, parent)
            for parent in parents
            if parent.prototype() == sp.Scalar
        ]
        has_budget = (
            len([scalar for scalar in scalars if scalar.is_privacy_params()])
            == 1
        )
        has_seed = (
            len([scalar for scalar in scalars if scalar.is_random_seed()]) == 1
        )
        return has_budget and has_seed

    def is_synthetic(self, dataspec: st.DataSpec) -> bool:
        """Return True if the dataspec is synthetic.

        This functions creates a VariantConstraint on the DataSpec to cache
        the SYNTHETIC constraint.
        """
        # TODO fetch real context and epsilon
        public_context: Collection[str] = []
        privacy_limit = None
        kind = st.ConstraintKind.SYNTHETIC

        # Does any saved constraint yet verifies that the Dataspec is synthetic
        for constraint in self.verified_constraints(dataspec):
            if self.verifies(constraint, kind, public_context, privacy_limit):
                return True

        # Determine is the Dataspec is synthetic
        if dataspec.is_transformed():
            transform = dataspec.transform()
            if transform.protobuf().spec.HasField("synthetic"):
                is_synthetic = True
            else:
                # Returns true if the DataSpec derives only from synthetic
                args_parents, kwargs_parents = dataspec.parents()
                is_synthetic = all(
                    [self.is_synthetic(ds) for ds in args_parents]
                    + [self.is_synthetic(ds) for ds in kwargs_parents.values()]
                )
        else:
            is_synthetic = False

        # save variant constraint
        if is_synthetic:
            syn_constraint(dataspec)

        return is_synthetic

    def is_public(self, dataspec: st.DataSpec) -> bool:
        """Return True if the dataspec is public.

        Some DataSpecs are intrinsically Public, this is the case if they are
        freely available externally, they can be tagged so and will never be
        considered otherwise.

        This function returns True in the following cases:
        - The dataspec is an ML model
        - The dataspec is transformed but all its inputs are public

        This functions creates a VariantConstraint on the DataSpec to cache the
        PUBLIC constraint.
        """
        # TODO fetch real context and epsilon
        public_context: Collection[str] = []
        privacy_limit = DeltaEpsilonLimit({0.0: 0.0})
        kind = st.ConstraintKind.PUBLIC

        # Does any saved constraint yet verifies that the Dataspec is public
        for constraint in self.verified_constraints(dataspec):
            if self.verifies(constraint, kind, public_context, privacy_limit):
                return constraint.properties()[IS_PUBLIC] == str(True)

        # Determine is the Dataspec is public
        if dataspec.is_transformed():
            # Returns true if the DataSpec derives only from public
            args_parents, kwargs_parents = dataspec.parents()
            is_public = all(
                [self.is_public(ds) for ds in args_parents]
                + [self.is_public(ds) for ds in kwargs_parents.values()]
            )
        elif dataspec.prototype() == sp.Scalar:
            scalar = cast(st.Scalar, dataspec)
            assert (
                scalar.is_random_seed()
                or scalar.is_privacy_params()
                or scalar.is_synthetic_model()
            )
            is_public = True
        else:
            is_public = False

        # save variant constraint
        public_constraint(dataspec, is_public)

        return is_public

    def pep_token(self, dataspec: st.DataSpec) -> Optional[str]:
        """Return a token if the dataspec is PEP, otherwise return None.

        DataSpec.pep_token() returns a PEP token if the dataset is PEP and None
        otherwise. The PEP token is stored in the properties of the
        VariantConstraint. It is a hash initialized with a value when the
        Dataset is protected.

        If a transform does not preserve the PEID then the token is set to None
        If a transform preserves the PEID assignment but changes the rows (e.g.
        sample, shuffle, filter,...) then the token's value is changed If a
        transform does not change the rows (e.g. selecting a column, adding a
        scalar,...) then the token is passed without change

        A Dataspec is PEP if its PEP token is not None. Two PEP Dataspecs are
        aligned (i.e. they have the same number of rows and all their rows have
        the same PEID) if their tokens are equal.
        """
        if dataspec.prototype() == sp.Scalar:
            return None

        dataset = cast(st.Dataset, dataspec)

        # TODO fetch real context and budget
        public_context: Collection[str] = []
        privacy_limit = DeltaEpsilonLimit({0.0: 0.0})
        kind = st.ConstraintKind.PEP

        # Does any constraint yet verifies that the Dataset is PEP
        for constraint in self.verified_constraints(dataset):
            if self.verifies(constraint, kind, public_context, privacy_limit):
                stored_token = constraint.properties()[PEP_TOKEN]
                return None if stored_token == NO_TOKEN else stored_token

        # Compute the PEP token
        if not dataset.is_transformed():
            return None

        transform = dataset.transform()
        _, StaticChecker = routing.get_dataset_op(transform)
        pep_token = StaticChecker(dataset).pep_token(public_context)
        if pep_token is None:
            pep_token = NO_TOKEN

        pep_constraint(
            dataspec=dataset,
            token=pep_token,
            required_context=[],
            privacy_limit=privacy_limit,
        )

        return None if pep_token == NO_TOKEN else pep_token

    def private_queries(self, dataspec: st.DataSpec) -> List[st.PrivateQuery]:
        """Return the list of PrivateQueries used in a Dataspec's transform.

        It represents the privacy loss associated with the current computation.

        It can be used by Sarus when a user (Access object) reads a DP dataspec
        to update its accountant. Note that Private Query objects are generated
        with a random uuid so that even if they are submitted multiple times to
        an account, they are only accounted once (ask @cgastaud for more on
        accounting).
        """
        attribute = dataspec.attribute(name=PRIVATE_QUERY)
        # Already computed
        if attribute is not None:
            private_query_str = attribute[PRIVATE_QUERY]
            protos = [
                cast(ProtoPrivateQuery, dejson(q))
                for q in json.loads(private_query_str)
            ]
            return cast(
                List[st.PrivateQuery],
                BasePrivateQuery.from_protobuf(protos),
            )

        # Compute private queries
        if not dataspec.is_transformed():
            private_queries = []
        else:
            if dataspec.prototype() == sp.Dataset:
                dataset = cast(st.Dataset, dataspec)
                private_queries = sync(
                    routing.TransformedDataset(dataset).private_queries()
                )
            else:
                scalar = cast(st.Scalar, dataspec)
                private_queries = sync(
                    routing.TransformedScalar(scalar).private_queries()
                )

        # Cache in an attribute
        subqueries = [
            proto_to_json(query.protobuf()) for query in private_queries
        ]
        attach_properties(
            dataspec,
            properties={PRIVATE_QUERY: json.dumps(subqueries)},
            name=PRIVATE_QUERY,
        )

        return private_queries
