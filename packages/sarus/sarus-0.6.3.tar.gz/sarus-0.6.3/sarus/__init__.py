"""SDK classes and functions."""
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sarus import (
        numpy,
        pandas,
        pandas_profiling,
        plotly,
        sklearn,
        skopt,
        std,
        xgboost,
    )

    from .sarus import Client, Dataset
    from .utils import eval, eval_policy, floating, integer, length

VERSION = "0.6.3"

__all__ = [
    "Dataset",
    "Client",
    "length",
    "eval",
    "eval_policy",
    "config",
    "floating",
    "integer",
]
