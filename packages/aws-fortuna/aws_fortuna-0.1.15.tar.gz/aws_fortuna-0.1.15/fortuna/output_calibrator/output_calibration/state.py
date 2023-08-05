from __future__ import annotations

from typing import Any, Dict, Optional, Union

import jax.numpy as jnp
from flax.core import FrozenDict

from fortuna.training.train_state import TrainState
from fortuna.typing import CalibMutable, CalibParams, OptaxOptimizer
from fortuna.utils.strings import convert_string_to_jnp_array


class OutputCalibState(TrainState):
    params: CalibParams
    mutable: Optional[CalibMutable] = None
    encoded_name: jnp.ndarray = convert_string_to_jnp_array("OutputCalibState")

    @classmethod
    def init(
        cls,
        params: CalibParams,
        mutable: Optional[CalibMutable] = None,
        optimizer: Optional[OptaxOptimizer] = None,
        **kwargs,
    ) -> Any:
        """
        Initialize a output_calibration state.

        Parameters
        ----------
        params : CalibParams
            The output_calibration parameters.
        optimizer : Optional[OptaxOptimizer]
            An Optax optimizer associated with the output_calibration state.
        mutable : Optional[CalibMutable]
            The output_calibration mutable objects.

        Returns
        -------
        Any
            A output_calibration state.
        """
        return cls(
            apply_fn=None,
            params=params,
            opt_state=kwargs["opt_state"]
            if optimizer is None and "opt_state" in kwargs
            else None
            if optimizer is None
            else optimizer.init(params),
            mutable=mutable,
            step=kwargs.get("step", 0),
            tx=optimizer,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["opt_state", "apply_fn", "tx", "step"]
            },
        )

    @classmethod
    def init_from_dict(
        cls,
        d: Union[Dict, FrozenDict],
        optimizer: Optional[OptaxOptimizer] = None,
        **kwargs,
    ) -> OutputCalibState:
        """
        Initialize a output_calibration state from a dictionary.

        Parameters
        ----------
        d : Union[Dict, FrozenDict]
            A dictionary with as keys the calibrators and as values their initializations.
        optimizer : Optional[OptaxOptimizer]
            An optax optimizer to assign to the output_calibration state.

        Returns
        -------
        OutputCalibState
            A output_calibration state.
        """
        kwargs = {
            **kwargs,
            **{
                k: v
                for k, v in d.items()
                if k
                not in [
                    "params",
                    "mutable",
                    "optimizer",
                ]
            },
        }
        return cls.init(
            FrozenDict(d["params"]),
            FrozenDict(d["mutable"]),
            optimizer,
            **kwargs,
        )
