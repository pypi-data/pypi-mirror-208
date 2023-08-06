from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

import numpy as np

from sarus_data_spec.dataspec_validator.signature import (
    SarusBoundSignature,
    SarusParameter,
    SarusSignature,
)

from .external_op import ExternalOpImplementation

try:
    import xgboost
except ModuleNotFoundError:
    pass  # error message in typing.py


class xgb_classifier(ExternalOpImplementation):
    _transform_id = "xgboost.XGB_CLASSIFIER"
    _signature = SarusSignature(
        SarusParameter(
            name="n_estimators",
            annotation=int,
            default=100,
        ),
        SarusParameter(
            name="max_depth",
            annotation=Optional[int],
            default=None,
        ),
        SarusParameter(
            name="max_leaves",
            annotation=Optional[int],
            default=None,
        ),
        SarusParameter(
            name="max_bin",
            annotation=Optional[int],
            default=None,
        ),
        SarusParameter(
            name="grow_policy",
            annotation=Optional[Literal[0, 1]],
            default=None,
        ),
        SarusParameter(
            name="learning_rate",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="verbosity",
            annotation=Optional[int],
            default=None,
        ),
        SarusParameter(
            name="objective",
            annotation=Optional[Union[str, Callable]],
            default=None,
        ),
        SarusParameter(
            name="booster",
            annotation=Optional[str],
            default=None,
        ),
        SarusParameter(
            name="tree_method",
            annotation=Optional[str],
            default=None,
        ),
        SarusParameter(
            name="n_jobs",
            annotation=Optional[int],
            default=None,
            predicate=lambda x: x is None,
        ),
        SarusParameter(
            name="gamma",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="min_child_weight",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="max_delta_step",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="subsample",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="colsample_bytree",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="colsample_bylevel",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="colsample_bynode",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="reg_alpha",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="reg_lambda",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="scale_pos_weight",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="base_score",
            annotation=Optional[float],
            default=None,
        ),
        SarusParameter(
            name="random_state",
            annotation=Optional[Union[np.random.RandomState, int]],
            default=None,
        ),
        SarusParameter(
            name="missing",
            annotation=float,
            default=np.nan,
        ),
        SarusParameter(
            name="num_parallel_tree",
            annotation=Optional[int],
            default=None,
        ),
        SarusParameter(
            name="monotone_constraints",
            annotation=Optional[Union[Dict[str, int], str]],
            default=None,
        ),
        SarusParameter(
            name="interaction_constraints",
            annotation=Optional[Union[str, List[Tuple[str]]]],
            default=None,
        ),
        SarusParameter(
            name="importance_type",
            annotation=Optional[str],
            default=None,
        ),
        SarusParameter(
            name="gpu_id",
            annotation=Optional[int],
            default=None,
            predicate=lambda x: x is None,
        ),
        SarusParameter(
            name="validate_parameters",
            annotation=Optional[bool],
            default=None,
        ),
        SarusParameter(
            name="predictor",
            annotation=Optional[str],
            default=None,
        ),
        SarusParameter(
            name="enable_categorical",
            annotation=bool,
            default=False,
        ),
        SarusParameter(
            name="max_cat_to_onehot",
            annotation=Optional[int],
            default=None,
        ),
        SarusParameter(
            name="max_cat_threshold",
            annotation=Optional[str],
            default=None,
        ),
        SarusParameter(
            name="eval_metric",
            annotation=Optional[Union[str, List[str], Callable]],
            default=None,
        ),
        SarusParameter(
            name="early_stopping_rounds",
            annotation=Optional[str],
            default=None,
        ),
        SarusParameter(
            name="callbacks",
            annotation=Optional[List[Callable]],
            default=None,
            predicate=lambda x: x is None,
        ),
        SarusParameter(
            name="kwargs",
            annotation=Optional[Dict],
            default=None,
        ),
        SarusParameter(
            name="use_label_encoder",
            annotation=Optional[bool],
            default=None,
        ),
    )

    async def call(self, signature: SarusBoundSignature) -> Any:
        kwargs = await signature.collect_kwargs()
        return xgboost.XGBClassifier(**kwargs)
