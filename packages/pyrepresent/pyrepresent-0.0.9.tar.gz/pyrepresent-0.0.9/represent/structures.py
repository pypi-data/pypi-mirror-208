# structures.py

import datetime as dt
from typing import Union, Any, Optional, Callable
from functools import wraps

from colorama import Fore, Style

import pandas as pd
import numpy as np

from represent.base import is_proxy_process

__all__ = [
    "Colors",
    "DataStructure",
    "DataStructureMeta",
    "DictStructure",
    "HiddenStructure",
    "SetStructure",
    "StringWrapper",
    "ListStructure",
    "CircularReferenceStructure",
    "TupleStructure",
    "structures",
    "structure_types",
    "colorize",
    "decolorize",
    "TypeStructure",
    "ObjectStructure"
]

Args = Kwargs = Any

class Colors:
    """A class to represent colors."""

    RED = "$RED$"
    BLACK = "$BLACK$"
    GREEN = "$GREEN$"
    WHITE = "$WHITE$"
    BLUE = "$BLUE$"
    YELLOW = "$YELLOW$"
    MAGENTA = "$MAGENTA$"
    CYAN = "$CYAN$"
    END = "$END$"

    colors = {
        RED: Fore.RED,
        GREEN: Fore.GREEN,
        BLUE: Fore.BLUE,
        YELLOW: Fore.YELLOW,
        MAGENTA: Fore.MAGENTA,
        CYAN: Fore.CYAN,
        BLACK: Fore.BLACK,
        WHITE: Fore.WHITE,
        END: Style.RESET_ALL
    }

    @staticmethod
    def color_repr_address(content: str, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        return (
            content.
            replace("<", f"{Colors.RED}<{Colors.END}").
            replace(">", f"{Colors.RED}>{Colors.END}")
        )
    # end color_repr_address

    @staticmethod
    def color_class(content: str, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        name = content

        return (
            name[:name.rfind(".") + 1] +
            Colors.CYAN +
            name[name.rfind(".") + 1:len(name) + name.find("(") + 1] +
            Colors.END +
            name[len(name) + name.find("(") + 1:]
        )
    # end color_repr_class

    @staticmethod
    def color_repr_class(content: str, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        name = content

        return (
            name[:name.rfind(".") + 1] +
            Colors.CYAN +
            name[name.rfind(".") + 1:name.find(" object at")] +
            Colors.END +
            name[name.find(" object at"):]
        )
    # end color_repr_class

    @staticmethod
    def color_repr(content: str, value: Any, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param value: The object.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        name = Colors.color_repr_address(content, color=color)

        address = f"0x00000{str(hex(id(value))).upper()[2:]}"

        name = (
            name[:name.find(f" {address}") + 1] +
            Colors.MAGENTA +
            name[
                name.find(f" {address}") + 1:
                name.find(f" {address}") + len(f" {address}")
            ] +
            Colors.END + name[
                name.find(f" {address}") + len(f" {address}"):
            ]
        )

        name = Colors.color_repr_class(name, color=color)

        return name
    # end color_repr

    @staticmethod
    def color_hidden_value(content: str, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        return f"{Colors.RED}{content}{Colors.END}"
    # end color_hidden_value

    @staticmethod
    def color_builtin_value(content: str, value: Any, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param value: The object.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        try:
            color = {
                str: Colors.YELLOW,
                int: Colors.MAGENTA,
                float: Colors.MAGENTA,
                dt.timedelta: Colors.MAGENTA,
                bool: Colors.CYAN,
                type(None): Colors.CYAN
            }[type(value)]

            if type(value) == str:
                chars = ["/", "\\", r"\t", r"\n"]
                content = "".join(
                    f"{color}{char}{Colors.END}"
                    if char not in chars
                    else char for char in content
                )
                content = content.replace(
                    ":\\", f"{Colors.MAGENTA}:\\{Colors.END}"
                )
                content = content.replace(
                    f"{color}:{Colors.END}\\",
                    f"{Colors.MAGENTA}:\\{Colors.END}"
                )

                for char in chars:
                    content = content.replace(
                        char, f"{Colors.MAGENTA}{char}{Colors.END}"
                    )
                # end for

                return content

            elif type(value) == dt.timedelta:
                content = "".join(
                    f"{color}{char}{Colors.END}"
                    if char != ":"
                    else char for char in content
                )
                content = content.replace(
                    ":", f"{Colors.RED}:{Colors.END}"
                )

                return content

            else:
                return f"{color}{content}{Colors.END}"
            # end if

        except KeyError:
            return content
        # end try
    # end color_builtin_value

    @staticmethod
    def color_key_name(content: str, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        return Colors.color_builtin_value(
            content=content, color=color, value=""
        )
    # end color_key_name

    @staticmethod
    def color_attribute_name(content: str, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        return f"{Colors.WHITE}{content}{Colors.END}"
    # end color_attribute_name

    @staticmethod
    def color_pairing_operator(content: str, color: Optional[bool] = True) -> str:
        """
        Colors the string of the object's repr.

        :param content: The string to color.
        :param color: The value to color the content.

        :return: The colored repr string
        """

        if not color:
            return content
        # end if

        return f"{Colors.RED}{content}{Colors.END}"
    # end color_pairing_operator
# end Colors

def construct(constructor: Callable) -> Callable:
    """
    Wraps the constructor of the model class.

    :param constructor: The init method of the class.

    :return: The wrapped init method.
    """

    @wraps(constructor)
    def __str__(*args: Args, **kwargs: Kwargs) -> str:
        """
        Defines the class attributes to wrap the init method.

        :param args: Any positional arguments.
        :param kwargs: Any keyword arguments

        :returns: The model object.
        """

        try:
            return constructor(*args, **kwargs).replace("END$$(", Colors.END)

        except RecursionError:
            return repr(CircularReferenceStructure(*args, **kwargs))
        # end try
    # end __str__

    return __str__
# end construct

class DataStructureMeta(type):
    """A class to create the data structure classes."""

    def __init__(cls, name, bases, attr_dict) -> None:
        """
        Defines the class attributes.

        :param name: The type name.
        :param bases: The valid_bases of the type.
        :param attr_dict: The attributes of the type.
        """

        super().__init__(name, bases, attr_dict)

        cls.__str__ = construct(cls.__str__)
    # end __init__
# end DataStructureMeta

class DataStructure(metaclass=DataStructureMeta):
    """A class to represent a structure."""

    __type__ = None
    __value__ = None
    __class__ = False

    # noinspection PyBroadException
    try:
        color = is_proxy_process()

    except Exception:
        color = True
    # end try

    def __repr__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        return str(self)
    # end if

    @property
    def name(self) -> str:
        """
        Returns the name of the object.

        :return: The name string.
        """

        if self.__value__ is None:
            name = (
                str(self.__type__).
                replace("<class '", "").
                replace("'>", "")
            ) if not self.__class__ else self.__value__

            return Colors.color_class(name, color=self.color)

        else:
            name = repr(self.__value__)

            return Colors.color_repr(
                name, self.__value__, color=self.color
            )
        # end if
    # end name
# end DataStructure

class TypeStructure(DataStructure):
    """A class to represent a structure."""

    def __init__(self, value: type) -> None:
        """
        Defines the class attributes.

        :param value: The value to hold.
        """

        self.value = value
    # end __init__

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        data = Colors.color_class(repr(self.value).replace("'", ''))
        data = data.replace('<class', f"<{Colors.CYAN}class{Colors.END} ")
        data = Colors.color_repr_address(data)

        return data
    # end __str__
# end TypeStructure

class ObjectStructure(DataStructure):
    """A class to represent a structure."""

    def __init__(self, value: object) -> None:
        """
        Defines the class attributes.

        :param value: The value to hold.
        """

        self.value = value
    # end __init__

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        string = (
            f"<{type(self.value).__module__}."
            f"{type(self.value).__name__} "
            f"object at 0x00000{str(hex(id(self.value))).upper()[2:]}>"
        )

        data = Colors.color_class(string)
        data = Colors.color_repr_address(data)
        data = Colors.color_repr(data, self.value)

        content = ""

        if isinstance(self.value, pd.DataFrame):
            content = ', '.join([f'|{row}|' for row in str(self.value).split('\n')])

        elif isinstance(self.value, np.ndarray):
            # noinspection PyUnresolvedReferences
            content = str(self.value.tolist())
        # end if

        return f"{data}({content})"
    # end __str__
# end ObjectStructure

class SetStructure(DataStructure, set):
    """A class to represent a structure."""

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        content = ', '.join(
            [
                Colors.color_builtin_value(
                    str(value) if (type(value) != str) else repr(value),
                    value, color=self.color
                )
                for value in self
            ]
        )

        if self.__type__ is None:
            return "{" + content + "}"
        # end if

        return f"{self.name}({content})"
    # end __str__
# end SetStructure

class DictStructure(DataStructure, dict):
    """A class to represent a structure."""

    _hash = None

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        if self.__type__ is None:
            separator = ": "
            wrapper = "'"

        else:
            separator = "="
            wrapper = ""
        # end if

        separator = Colors.color_pairing_operator(
            separator, color=self.color
        )

        content = ', '.join(
            [
                (
                    str(key) if (type(key) != str)
                    else (
                        Colors.color_key_name(
                            f"{wrapper}{key}{wrapper}", color=self.color
                        )
                        if wrapper == "'" else
                        Colors.color_attribute_name(
                            f"{wrapper}{key}{wrapper}", color=self.color
                        )
                    )
                ) + separator +
                Colors.color_builtin_value(
                    str(value) if (type(value) != str) else repr(value),
                    value, color=self.color
                )
                for key, value in self.items()
            ]
        )

        if self.__type__ is None:
            return "{" + content + "}"
        # end if

        return f"{self.name}({content})"
    # end __str__

    def __hash__(self) -> int:
        """
        Creates the hash for the object.

        :return: The hash for the data.
        """

        if self._hash is None:
            hash_ = 0

            for pair in self.items():
                hash_ ^= hash(pair)
            # end for

            self._hash = hash_
        # end if

        return self._hash
# end DictStructure

class ListStructure(DataStructure, list):
    """A class to represent a structure."""

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        content = ', '.join(
            [
                Colors.color_builtin_value(
                    str(value) if (type(value) != str) else repr(value),
                    value, color=self.color
                )
                for value in self
            ]
        )

        if self.__type__ is None:
            return "[" + content + "]"
        # end if

        return f"{self.name}({content})"
    # end __str__
# end ListStructure

class TupleStructure(DataStructure, tuple):
    """A class to represent a structure."""

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        content = ', '.join(
            [
                Colors.color_builtin_value(
                    str(value) if (type(value) != str) else repr(value),
                    value, color=self.color
                )
                for value in self
            ]
        )

        if self.__type__ is None:
            return "(" + content + ")"
        # end if

        return f"{self.name}({content})"
    # end __str__
# end TupleStructure

class HiddenStructure(DataStructure):
    """A class to represent a structure."""

    __type__ = str

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        return "..."
    # end __str__
# end HiddenStructure

class StringWrapper(DataStructure):
    """A class to represent a structure."""

    __type__ = str

    def __init__(self, value: str) -> None:
        """
        Defines the class attributes.

        :param value: The value to hold.
        """

        self.value = value
    # end __init__

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        return self.value
    # end __str__
# end StringWrapper

class CircularReferenceStructure(DataStructure):
    """A class to represent a structure."""

    def __init__(self, value: Any) -> None:
        """
        Defines the class attributes.

        :param value: The value to hold.
        """

        self.__value__ = value

        self.__type__ = type(self.__value__)
    # end __init__

    def __str__(self) -> str:
        """
        Returns a string to represent the object.

        :return: A string representation for the commands of the object.
        """

        return Colors.color_repr_address(
            f"<circular referenced object: {self.name}>", color=self.color
        )
    # end __str__
# end CircularReferenceStructure

def colorize(content: str, /) -> str:
    """
    Colors the string with the pre-written color codes.

    :param content: The string to color.

    :return: The colored string.
    """

    for key, value in Colors.colors.items():
        content = content.replace(key, value)
    # end for

    return content
# end colorize

def decolorize(content: str, /) -> str:
    """
    Colors the string with the pre-written color codes.

    :param content: The string to color.

    :return: The colored string.
    """

    for key, value in Colors.colors.items():
        content = content.replace(key, "")
        content = content.replace(value, "")
    # end for

    return content
# end uncolor

Structure = Union[
    SetStructure, DictStructure, ListStructure, TupleStructure
]
structures = {
    set: SetStructure, list: ListStructure,
    tuple: TupleStructure, dict: DictStructure,
    type: TypeStructure
}

structure_types = (
    SetStructure, DictStructure, ListStructure, TupleStructure
)