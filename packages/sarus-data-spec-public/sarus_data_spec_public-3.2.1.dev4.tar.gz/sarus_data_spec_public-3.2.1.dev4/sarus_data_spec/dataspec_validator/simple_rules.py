from typing import Collection, List, Optional, Tuple, cast
import logging

import sarus_data_spec.typing as st

ArgStruct = Tuple[List[int], List[str]]
logger = logging.getLogger(__name__)


def verifies(
    variant_constraint: st.VariantConstraint,
    kind: st.ConstraintKind,
    public_context: Collection[str],
    privacy_limit: Optional[st.PrivacyLimit],
) -> bool:
    if kind == st.ConstraintKind.PUBLIC:
        return verifies_public(variant_constraint=variant_constraint)

    elif kind == st.ConstraintKind.SYNTHETIC:
        return verifies_synthetic(variant_constraint=variant_constraint)

    elif kind == st.ConstraintKind.MOCK:
        return verifies_mock(variant_constraint=variant_constraint)

    elif kind == st.ConstraintKind.DP:
        return verifies_dp(
            variant_constraint=variant_constraint,
            privacy_limit=privacy_limit,
        )

    else:  # kind == st.ConstraintKind.PEP:
        return verifies_pep(variant_constraint=variant_constraint)


def verifies_public(variant_constraint: st.VariantConstraint) -> bool:
    return variant_constraint.constraint_kind() == st.ConstraintKind.PUBLIC


def verifies_synthetic(variant_constraint: st.VariantConstraint) -> bool:
    return variant_constraint.constraint_kind() in [
        st.ConstraintKind.PUBLIC,
        st.ConstraintKind.SYNTHETIC,
    ]


def verifies_mock(variant_constraint: st.VariantConstraint) -> bool:
    return variant_constraint.constraint_kind() in [
        st.ConstraintKind.PUBLIC,
        st.ConstraintKind.MOCK,
    ]


def verifies_pep(
    variant_constraint: st.VariantConstraint,
) -> bool:
    """If we attached a PEP constraint to a dataspec then it is PEP.

    NB: for now we don't check the context nor the privacy limit
    """
    return variant_constraint.constraint_kind() == st.ConstraintKind.PEP


def verifies_dp(
    variant_constraint: st.VariantConstraint,
    privacy_limit: Optional[st.PrivacyLimit],
) -> bool:
    """Check if a variant constraint satisfies a DP profile.

    For now, return True only for strict equality.
    """
    if privacy_limit is None:
        raise ValueError(
            "Input privacy limit required when checking against DP."
        )

    kind = variant_constraint.constraint_kind()
    if kind != st.ConstraintKind.DP:
        return False

    constraint_privacy_limit = variant_constraint.privacy_limit()
    if constraint_privacy_limit is None:
        raise ValueError(
            "Found a DP constraint without a privacy limit "
            "when checking against DP."
        )

    return cast(
        bool,
        privacy_limit.delta_epsilon_dict()
        == constraint_privacy_limit.delta_epsilon_dict(),
    )
