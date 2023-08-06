import inspect
import logging
import os
from functools import partial, wraps
from typing import Any, Callable, Dict, Optional, Type

import sarus_data_spec.typing as st
import yaml
from sarus_data_spec.context import global_context
from sarus_data_spec.transform import external

from .context.typing import LocalSDKContext
from .typing import DataSpecVariant, DataSpecWrapper

logger = logging.getLogger(__name__)

config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_file) as f:
    config = yaml.load(f.read(), Loader=yaml.Loader)


def module_config(module_name: str) -> Optional[Dict[str, Any]]:
    """Fetch the module's configuration from the config dict."""
    keys = module_name.split(".")
    module_conf = config
    for key in keys:
        if module_conf is None:
            return
        module_conf = module_conf.get(key)
    return module_conf


def eval(
    x: Any,
    target_epsilon: Optional[float] = None,
    verbose: Optional[int] = None,
) -> st.DataSpecValue:
    """Recursively evaluates DataSpecWrappers to values."""
    if isinstance(x, DataSpecWrapper):
        return x.__sarus_eval__(target_epsilon, verbose)

    if target_epsilon is not None:
        logger.warning(
            "Ignoring `target_epsilon` since the evaluated object"
            " is not a Sarus object."
        )

    if isinstance(x, list):
        return [eval(x_) for x_ in x]
    elif isinstance(x, tuple):
        return tuple([eval(x_) for x_ in x])
    elif isinstance(x, dict):
        return {eval(k): eval(v) for k, v in x.items()}
    else:
        return x


def save(dw: DataSpecWrapper, path: str) -> None:
    """Save a DataSpecWrapper for loading in another notebook."""
    dw.sarus_save(path)


def convert_container(x: Any) -> Any:
    """Recursively convert containers in DataSpecWrappers if one
    element is a DataSpecWrapper."""
    from sarus.std import Dict, List, Set, Slice, Tuple

    if isinstance(x, DataSpecWrapper):
        return x
    elif isinstance(x, list):
        elems = [convert_container(e) for e in x]
        if any(isinstance(e, DataSpecWrapper) for e in elems):
            return List(*elems)
        else:
            return x
    elif isinstance(x, set):
        elems = [convert_container(e) for e in x]
        if any(isinstance(e, DataSpecWrapper) for e in elems):
            return Set(*elems)
        else:
            return x
    elif isinstance(x, tuple):
        elems = [convert_container(e) for e in x]
        if any(isinstance(e, DataSpecWrapper) for e in elems):
            return Tuple(*elems)
        else:
            return x
    elif isinstance(x, dict):
        elems = {k: convert_container(v) for k, v in x.items()}
        if any(isinstance(e, DataSpecWrapper) for e in elems.values()):
            return Dict(**elems)
        else:
            return x
    elif isinstance(x, slice):
        elems = [
            x.start,
            x.stop,
            x.step,
        ]
        if any([isinstance(e, DataSpecWrapper) for e in elems]):
            return Slice(*elems)
        else:
            return x
    else:
        return eval(x)


def eval_policy(x: Any) -> Optional[str]:
    """The alternative dataspec's privacy policy."""
    if isinstance(x, DataSpecWrapper):
        return x.__eval_policy__()
    else:
        return None


_registered_methods = []
_registered_functions = []


class register_method:
    """This decorator method allows to register methods declared in classes.

    It uses this behavior since Python 3.6
    https://docs.python.org/3/reference/datamodel.html#object.__set_name__
    """

    def __init__(self, method: Callable, code_name: str) -> None:
        self.method = method
        self.code_name = code_name

    def __set_name__(self, owner: Type, name: str) -> None:
        global _registered_methods
        _registered_methods.append(
            (owner.__module__, owner.__name__, name, self.code_name)
        )
        setattr(owner, name, self.method)


def register_ops():
    """Monkey-patching standard libraries to have Sarus functions.

    This functions is intended to be called in a Sarus module. The module's
    local variables will be modified dynamically (monkey patching) to replace
    some functions or methods by Sarus equivalent operations.

    Technically, we get the previous frame's (the module where the function is
    called) locals mapping and update it.

    The modified methods and functions are listed in the `sarus/config.yaml`
    file.
    """
    previous_frame = inspect.currentframe().f_back
    local_vars = previous_frame.f_locals
    module_name = local_vars["__name__"]
    module_conf = module_config(module_name)
    if module_conf is None:
        return

    # Registering module functions
    global _registered_functions
    functions = module_conf.get("sarus_functions", {})
    for fn_name, fn_code_name in functions.items():
        local_vars[fn_name] = create_function(
            fn_code_name, module_name, fn_name
        )

    # Registering explicit evaluation functions
    explicit_eval_fns = module_conf.get("explicit_eval", [])
    for fn_name in explicit_eval_fns:
        fn_obj = local_vars[fn_name]
        local_vars[fn_name] = explicit_sarus_eval(fn_obj)

    # Registering classes methods
    global _registered_methods
    classes = module_conf.get("classes", {})
    for class_name, methods in classes.items():
        class_obj = local_vars[class_name]
        for mth_name, mth_code_name in methods.items():
            setattr(
                class_obj,
                mth_name,
                create_method(
                    mth_code_name, module_name, class_name, mth_name
                ),
            )


def serialize_external(
    code_name: str, *args: Any, **kwargs: Any
) -> st.DataSpec:
    """Some arguments are instances of DataSpecWrapper and others are
    just Python object. This function registers a new dataspec."""
    args = [convert_container(arg) for arg in args]
    kwargs = {
        eval(name): convert_container(arg) for name, arg in kwargs.items()
    }
    py_args = {
        i: arg
        for i, arg in enumerate(args)
        if not isinstance(arg, DataSpecWrapper)
    }
    ds_args_pos = [
        i for i, arg in enumerate(args) if isinstance(arg, DataSpecWrapper)
    ]
    ds_arg_types = {
        i: str(arg.__wraps__)
        for i, arg in enumerate(args)
        if isinstance(arg, DataSpecWrapper)
    }
    ds_args = [
        arg.dataspec(DataSpecVariant.USER_DEFINED)
        for arg in args
        if isinstance(arg, DataSpecWrapper)
    ]
    py_kwargs = {
        name: arg
        for name, arg in kwargs.items()
        if not isinstance(arg, DataSpecWrapper)
    }
    ds_kwargs = {
        name: arg.dataspec(DataSpecVariant.USER_DEFINED)
        for name, arg in kwargs.items()
        if isinstance(arg, DataSpecWrapper)
    }
    ds_kwargs_types = {
        name: str(arg.__wraps__)
        for name, arg in kwargs.items()
        if isinstance(arg, DataSpecWrapper)
    }
    transform = external(
        id=code_name,
        py_args=py_args,
        py_kwargs=py_kwargs,
        ds_args_pos=ds_args_pos,
        ds_types={**ds_arg_types, **ds_kwargs_types},
    )
    new_dataspec = transform(*ds_args, **ds_kwargs)
    return new_dataspec


def _sarus_op(
    code_name: str,
    inplace: bool = False,
    register: bool = False,
    is_property: bool = False,
):
    """Parametrized decorator to register a Sarus external op."""

    def parametrized_wrapper(ops_fn):
        @wraps(ops_fn)
        def wrapper_fn(*args, **kwargs):
            new_dataspec = serialize_external(code_name, *args, **kwargs)
            context: LocalSDKContext = global_context()

            new_dataspec_wrapper = context.wrapper_factory().create(
                new_dataspec
            )

            if inplace:
                self: DataSpecWrapper = args[0]  # TODO check semantic
                self._set_dataspec(new_dataspec)

            return new_dataspec_wrapper

        if is_property:
            wrapper_fn = property(wrapper_fn)

        if register:
            wrapper_fn = register_method(wrapper_fn, code_name)

        return wrapper_fn

    return parametrized_wrapper


sarus_method = partial(_sarus_op, register=True, is_property=False)
sarus_property = partial(_sarus_op, register=True, is_property=True)


def sarus_init(code_name):
    """Decorator to initialize DataSpecWrapper classes from ops."""

    def parametrized_wrapper(ops_fn):
        @wraps(ops_fn)
        def wrapper_fn(self, *args, **kwargs):
            new_dataspec = serialize_external(code_name, *args, **kwargs)
            self._set_dataspec(new_dataspec)

        wrapper_fn = register_method(wrapper_fn, code_name)

        return wrapper_fn

    return parametrized_wrapper


def create_function(
    code_name: str, module_name: str, fn_name: str, inplace: bool = False
) -> Callable:
    """Create an op and register it as a function in a module."""
    global _registered_functions
    _registered_functions.append((module_name, fn_name, code_name))

    @_sarus_op(code_name=code_name, inplace=inplace)
    def dummy_fn(*args, **kwargs):
        ...

    return dummy_fn


def create_method(
    code_name: str,
    module_name: str,
    class_name: str,
    method_name: str,
    inplace: bool = False,
) -> Callable:
    """Create an op and register it as a method of a class."""
    global _registered_methods
    _registered_methods.append(
        (module_name, class_name, method_name, code_name)
    )

    @_sarus_op(code_name=code_name, inplace=inplace)
    def dummy_fn(*args, **kwargs):
        ...

    return dummy_fn


def create_lambda_op(code_name: str, inplace: bool = False) -> Callable:
    """Create an op and do not register it."""

    @_sarus_op(code_name=code_name, inplace=inplace)
    def dummy_fn(*args, **kwargs):
        ...

    return dummy_fn


@_sarus_op(code_name="std.LEN")
def length(__o: object):
    ...


@_sarus_op(code_name="std.INT")
def integer(__o: object):
    ...


@_sarus_op(code_name="std.FLOAT")
def floating(__o: object):
    ...


def explicit_sarus_eval(func):
    """Decorator to explicitly collect Dataspec's values before calling."""

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        args = [eval(arg) for arg in args]
        kwargs = {key: eval(val) for key, val in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped_func


def init_wrapped(wrapper_class):
    """Define the constructor to return a wrapped instance."""
    assert issubclass(wrapper_class, DataSpecWrapper)

    def __new__(cls, *args, **kwargs):
        return wrapper_class.__wraps__(*args, **kwargs)

    wrapper_class.__new__ = staticmethod(__new__)

    return wrapper_class
