#
# Copyright 2023 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
# pylint: disable=cyclic-import
import functools
from inspect import Parameter, signature
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from mypy_extensions import DefaultNamedArg, KwArg, VarArg
from typing_extensions import ParamSpec

from datarobot.enums import UseCaseReferenceEntityMap
from datarobot.errors import InvalidUsageError
from datarobot.models.use_cases.use_case import UseCase

from ...context import Context

P = ParamSpec("P")
T = TypeVar("T")


def resolve_use_case(
    params: Dict[str, Any],
    use_case_id: Optional[Union[str, List[str]]] = None,
    use_case_key: str = "experiment_container_id",
) -> Dict[str, Any]:
    """
    Add a global Use Case ID to query params for a list operation if no use_case_id has been passed
    This method supports checking for `use_case_id` in a params dict if users can build their own params dict.
    Parameters
    ----------
    params : Dict[str, Any]
        The query params dict to add a Use Case ID to, if a global ID exists, or if one was passed in directly.
    use_case_id : Optional[Union[str, List[str]]]
        Optional. The use case ID to add to a query params dict.
    use_case_key : Optional[str]
        Optional. The key that will be used in the query params for Use Case ID. Default is 'experiment_container_id'.
    Returns
    -------
    params : Dict[str, Any]
        If a Use Case ID is available, the params with the ID added. Otherwise, return the dict unmodified.
    """
    # Check to see if a use_case_id is already in the params dict
    if not params.get(use_case_key):
        # If use_case_id is not in the dict, add in the manually passed value, if it exists
        if use_case_id:
            params[use_case_key] = use_case_id
        elif Context.use_case:
            params[use_case_key] = Context.use_case.id  # type: ignore[union-attr]
    return params


def resolve_use_case_ids(use_cases: Union[List[UseCase], UseCase, List[str], str]) -> List[str]:
    """
    A helper function to convert a list of UseCase objects, single UseCase, or single Use Case ID
    into a list of strings.

    Parameters
    ----------
    use_cases : List[UseCase], UseCase, List[str], str
        The list of UseCase objects, list of strings, single UseCase object, or single Use Case ID to turn into
        a list of ID strings.

    Returns
    -------
    use_case_ids : List[str]
        The returned list of ID strings.
    """
    if isinstance(use_cases, list):
        return [
            use_case.id if isinstance(use_case, UseCase) else use_case for use_case in use_cases
        ]
    if isinstance(use_cases, UseCase):
        return [use_cases.id]
    else:
        return [use_cases]


def add_to_use_case(
    func: Callable[P, T]
) -> Callable[
    [
        VarArg(Any),
        DefaultNamedArg(Optional[Union[List[UseCase], UseCase, List[str], str]]),
        KwArg(Any),
    ],
    T,
]:
    """
    A decorator to mark functions as adding the return value to a given Use Case. When implemented,
    the decorator will add a `use_cases` keyword-only argument to the decorated function or method that
    will automatically add the returned object to a Use Case.

    Examples
    --------
    This decorator should only be added to methods that return a type listed in
    enums.UseCaseEntityType or enums.UseCaseExtendedEntityType.
    The function needs to have the return annotation added.

    This function could be decorated:
    .. code-block:: python
        def foo_bar() -> Dataset:
            ....
            return Dataset()

    These functions could not be decorated:
    .. code-block:: python
        def foo_bar():
            ....
            return Dataset()

        def foo_bar() -> Model:
            ....
            return Model()

    To decorate, it's as simple as adding the decorator. It's recommended to update the doc string for the
    method or function with:

    use_cases: list[UseCase] | UseCase | list[string] | string, optional
            A list of UseCase objects, UseCase object,
            list of Use Case ids or a single Use Case id to add this new <return_object_type> to. Must be a kwarg.

    So this:
    .. code-block:: python
        def foo_bar() -> Dataset:
            ....
            return Dataset()

    Would become this:
    .. code-block:: python
        @add_to_use_case
        def foo_bar() -> Dataset:
            \"\"\"
            use_cases: list[UseCase] | UseCase | list[string] | string, optional
            A list of UseCase objects, UseCase object,
            list of Use Case ids or a single Use Case id to add this new Dataset to. Must be a kwarg.
            \"\"\"
            ....
            return Dataset()

    Returns
    -------
    func : callable
        The wrapped function
    """
    ret_sig = signature(func)
    ret_type = ret_sig.return_annotation
    # Check if return annotation is a string or a type. If it's a type, get the name and make it lowercase.
    # If the return annotation is a string, just make it lower case.
    # Some return types are "TDataset", others are Dataset<datarobot.Dataset>
    ret_type = ret_type.__name__.lower() if not isinstance(ret_type, str) else ret_type.lower()
    ret_type = ret_type.lstrip("t")
    if not UseCaseReferenceEntityMap.get(ret_type):
        raise InvalidUsageError(
            "This decorator can only support methods that return a "
            "Project, Dataset, Notebook, or Application instance."
        )
    new_kw_param = Parameter("use_cases", kind=Parameter.KEYWORD_ONLY, default=None)
    param_list = list(ret_sig.parameters.values())
    param_list.append(new_kw_param)
    new_sig = ret_sig.replace(parameters=param_list)
    func.__signature__ = new_sig  # type: ignore[attr-defined]

    @functools.wraps(func)
    def inner(
        *args: P.args,
        use_cases: Optional[Union[List[UseCase], UseCase, List[str], str]] = None,
        **kwargs: P.kwargs,
    ) -> T:
        """
        Parameters
        ----------
        use_cases: list[UseCase] | UseCase | list[string] | string, optional
            A list of UseCase objects, UseCase object,
            list of Use Case IDs or a single Use Case ID to add this new Dataset to. Must be a kwarg.
        """
        ret = func(*args, **kwargs)
        if use_cases is not None:
            use_case_ids = resolve_use_case_ids(use_cases=use_cases)
            for use_case_id in use_case_ids:
                use_case = UseCase.get(use_case_id=use_case_id)
                use_case.add(entity=ret)
        return ret

    return inner  # type: ignore[return-value]
