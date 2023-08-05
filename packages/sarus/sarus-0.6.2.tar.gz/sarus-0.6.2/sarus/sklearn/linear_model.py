from __future__ import annotations

import sarus_data_spec.protobuf as sp

from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import register_ops, sarus_init, sarus_method

try:
    import sklearn.linear_model as linear_model
    from sklearn.linear_model import *
except ModuleNotFoundError:
    pass  # error message in sarus_data_spec.typing


class LinearRegression(DataSpecWrapper[linear_model.LinearRegression]):
    @sarus_init("sklearn.SK_LINEAR_REGRESSION")
    def __init__(self, steps, *, memory=None, verbose=False):
        ...

    @sarus_method("sklearn.SK_FIT", inplace=True)
    def fit(self, X, y=None):
        ...


register_ops()
