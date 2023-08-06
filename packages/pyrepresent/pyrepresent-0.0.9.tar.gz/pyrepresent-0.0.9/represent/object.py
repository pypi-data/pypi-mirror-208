# object.py

import inspect
import builtins
import datetime as dt
from typing import (
    Any, Optional, Union, Iterable, Type, Dict
)

from represent.base import is_bound_method
from represent.indentation import indent
from represent.structures import (
    structures, HiddenStructure, StringWrapper, colorize,
    CircularReferenceStructure, DataStructure, TypeStructure,
    ObjectStructure
)

import pandas as pd
import numpy as np

__all__ = [
    "to_string",
    "BaseModel",
    "Modifiers",
    "unwrap",
    "DataContainer"
]

class DataContainer(dict):
    """A class to represent a data container."""

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Sets the attribute.

        :param key: The key to the attribute.
        :param value: The value of the attribute.
        """

        self[key] = value

        super().__setattr__(key, value)
    # end __setattr__
# end DataContainer

class Modifiers(DataContainer):
    """A class to represent the modifiers of structures."""

    def __init__(
            self, *,
            assign: Optional[bool] = None,
            excluded: Optional[Iterable[Any]] = None,
            hidden: Optional[Iterable[Any]] = None,
            protected: Optional[bool] = None,
            properties: Optional[Union[bool, Iterable[str]]] = None,
            force: Optional[bool] = None,
            legalize: Optional[bool] = None,
            defined: Optional[bool] = None
    ) -> None:
        """
        Defines the class attributes.

        :param assign: The value to assign a type name to each commands' structure.
        :param excluded: The valid_values to exclude from the commands structure.
        :param properties: The value to extract properties.
        :param protected: The value to extract protected attributes.
        :param legalize: The value to legalize the written valid_values to be strings.
        :param hidden: The valid_values of hidden keywords.
        :param force: The value to force the settings of the parsing.
        :param defined: The value to show only defined valid_values.
        """

        super().__init__()

        if assign is None:
            assign = True
        # end if

        if protected is None:
            protected = False
        # end if

        if legalize is None:
            legalize = False
        # end if

        if force is None:
            force = False
        # end if

        if defined is None:
            defined = True
        # end if

        self.assign = assign
        self.protected = protected
        self.legalize = legalize
        self.force = force
        self.defined = defined

        self.properties = list(properties or [])
        self.excluded = list(excluded or ['modifiers'])
        self.hidden = list(hidden or [])
    # end __init__
# end Modifiers

class BaseModel:
    """A class to represent a base model."""

    modifiers = Modifiers()

    def __str__(self) -> str:
        """
        Returns a string to represent the model commands and structure.

        :return: The string representation of the model.
        """

        return to_string(self)
    # end __str__
# end BaseModel

def unwrap(
        data: Any, /, *,
        hidden: Optional[Union[Dict[Any, Any], Iterable[Any]]] = None,
        assign: Optional[bool] = False,
        properties: Optional[bool] = False,
        protected: Optional[bool] = False,
        legalize: Optional[bool] = False,
        force: Optional[bool] = False,
        defined: Optional[bool] = None,
        excluded: Optional[Iterable[Union[str, Type]]] = None,
        ids: Optional[Dict[int, Any]] = None
) -> Any:
    """
    Unwraps the models to get the valid_values as dictionaries.

    :param assign: The value to assign a type name to each commands' structure.
    :param data: The commands to process.
    :param ids: The ids of the collected objects.
    :param excluded: The keys to exclude from the commands structure.
    :param properties: The value to extract properties.
    :param protected: The value to extract hidden attributes.
    :param legalize: The value to legalize the written valid_values to be strings.
    :param hidden: The valid_values of hidden keywords.
    :param force: The value to force the settings of the parsing.
    :param defined: The value to show only defined valid_values.

    :return: The dictionary of unwrapped objects.
    """

    if inspect.isclass(data):
        return TypeStructure(data)
    # end if

    if (
        isinstance(data, BaseModel) and
        hasattr(data, "modifiers") and
        isinstance(data.modifiers, Modifiers) and
        ids and (not force)
    ):
        modifiers = data.modifiers

        assign = modifiers.assign
        excluded = modifiers.excluded
        properties = modifiers.properties
        protected = modifiers.protected
        hidden = modifiers.hidden
        legalize = modifiers.legalize
        defined = modifiers.defined
    # end if

    ids = ids or {}

    if (not isinstance(hidden, dict)) and (hidden is not None):
        hide = True

    elif hidden is None:
        hide = False

        hidden = ()

    else:
        hide = False
    # end if

    if (data_id := id(data)) in ids:
        return ids[data_id]

    else:
        ids[data_id] = (
            data if (
                (data.__class__.__name__ in dir(builtins) + dir(dt)) or
                (data is None)
            )
            else (
                (
                    repr(CircularReferenceStructure(data))
                    if legalize else (
                        StringWrapper(repr(CircularReferenceStructure(data)))
                    )
                ) if (repr(data) != repr(HiddenStructure()))
                else (data if legalize else StringWrapper(data))
            )
        )
    # end if

    assignment = None

    bound = False

    if isinstance(data, (pd.DataFrame, np.ndarray)):
        return ObjectStructure(data) if not (legalize and assign) else data

    elif isinstance(data, (HiddenStructure, StringWrapper)):
        return repr(data) if legalize else StringWrapper(repr(data))

    elif hasattr(data, '__dict__'):
        assignment = data

        data = {
            **data.__dict__, **(
                {
                    name: getattr(data, name) for (name, value) in
                    inspect.getmembers(
                        type(data), lambda attribute: isinstance(
                            attribute, property
                        )
                    ) if (
                        properties and
                        (isinstance(properties, bool) or name in properties)
                    )
                } if properties else {}
            )
        }

    elif (
        inspect.isfunction(data) or
        inspect.ismethod(data) or
        inspect.isclass(data) or
        isinstance(
            data, (
                bool, int, float, str, dt.time,
                dt.timedelta, dt.datetime, dt.timezone
            )
        ) or
        (bound := is_bound_method(data)) or
        data is None
    ):
        if bound and legalize:
            data = repr(data)
        # end if

        return data
    # end if

    results = None

    if isinstance(data, dict):
        results = {}

        for key, value in data.items():
            if (
                (
                    isinstance(key, str) and
                    (
                        (not key.startswith("_")) or
                        (assignment is None) or
                        protected
                    )
                ) or (not isinstance(key, str))
            ):
                try:
                    bool_value = bool(value)

                except ValueError:
                    bool_value = True
                # end try

                if (
                    (excluded is not None) and
                    ((key in excluded) or (type(value) in excluded))
                ) or (
                    defined and not (isinstance(value, bool) or bool_value)
                ):
                    continue
                # end if

                if (
                    (hidden is not None) and
                    (key in hidden) and
                    (assignment is not None)
                ):
                    if not hide:
                        value = hidden[key]

                    else:
                        value = HiddenStructure()
                    # end if
                # end if

                if is_bound_method(key) and legalize:
                    key = repr(key)

                else:
                    key = unwrap(
                        key, assign=assign, ids=ids, excluded=excluded,
                        properties=properties, protected=protected,
                        hidden=hidden, legalize=legalize, force=force,
                        defined=defined
                    )
                # end if

                if not is_bound_method(value):
                    results[key] = unwrap(
                        value, assign=assign, ids=ids, excluded=excluded,
                        properties=properties, protected=protected,
                        hidden=hidden, legalize=legalize, force=force,
                        defined=defined
                    )

                else:
                    results[key] = repr(value) if legalize else value
                # end if
            # end if
        # end for

    elif isinstance(data, (tuple, list, set)):
        results = []

        for value in data:
            results.append(
                unwrap(
                    value, assign=assign, ids=ids, excluded=excluded,
                    properties=properties, protected=protected,
                    hidden=hidden, legalize=legalize, force=force,
                    defined=defined
                )
            )
        # end for

        results = type(data)(results)
    # end if

    if assign and (results is not None):
        results = structures[type(results)](results)
        results.__type__ = (
            type(assignment) if (assignment is not None) else None
        )

        if not legalize:
            results.__value__ = (
                assignment if (assignment is not None) else None
            )
        # end if
    # end if

    ids[data_id] = results

    return results
# end unwrap

def to_string(obj: Any, /, modifiers: Optional[Modifiers] = None) -> str:
    """
    Returns a string to represent the model commands and structure.

    :return: The string representation of the model.
    """

    if modifiers is None:
        if (
            isinstance(obj, BaseModel) and
            hasattr(obj, "modifiers") and
            isinstance(obj.modifiers, Modifiers)
        ):
            modifiers = obj.modifiers

        else:
            modifiers = Modifiers()
        # end if
    # end if

    data = indent(str(unwrap(obj, **modifiers)))

    if DataStructure.color:
        data = colorize(data)
    # end if

    return data
# end to_string