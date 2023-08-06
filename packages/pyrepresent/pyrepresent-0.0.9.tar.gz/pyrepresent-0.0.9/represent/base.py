# base.py

import gc
import os
import sys
import six
import importlib
import subprocess
from pathlib import Path
from typing import Optional, Any, Dict
import contextlib
import warnings

__all__ = [
    "is_proxy_process",
    "validate_requirement",
    "is_bound_method",
    "get_object_from_memory_address",
    "run_silent_command",
    "suppress",
    "documentation",
    "document",
    "virtualenv_interpreter_location",
    "activate_virtualenv_command"
]

def is_bound_method(value: Any, /) -> bool:
    """
    Checks whether an object is a bound method or not.

    :param value: The object to check.

    :return: The boolean value.
    """

    try:
        return six.get_method_self(value) is not None

    except AttributeError:
        return False
    # end try
# end is_bound_method

def get_object_from_memory_address(address: int) -> Any:
    """
    Gets the python object from the memory address.

    :param address: The id of the object.

    :return: The object.
    """

    for obj in gc.get_objects():
        if id(obj) == address:
            return obj
        # end if
    # end for

    raise MemoryError(
        f'No object found at memory address: {repr(address)} '
        f'(most likely because it was deleted).'
    )
    # end try
# end get_object_from_memory_address

def is_proxy_process() -> bool:
    """
    Returns True if the process is running from an IDE.

    :return: The boolean value.
    """

    shells = {
        "bash.exe", "cmd.exe", "powershell.exe",
        "WindowsTerminal.exe"
    }

    s = subprocess.check_output(
        [
            "tasklist", "/v", "/fo", "csv",
            "/nh", "/fi", f"PID eq {os.getppid()}"
        ]
    )

    entry = str(s).strip().strip('"').strip('b\'"').split('","')

    return not (entry and (entry[0] in shells))
# end is_proxy_process

def suppress() -> contextlib.redirect_stdout:
    """
    Suppresses the output.

    :return: The output suppressor.
    """

    with warnings.catch_warnings(record=True):
        warnings.simplefilter("ignore")

        return contextlib.redirect_stdout(None)
    # end catch_warnings
# end suppress

def run_silent_command(command: str) -> None:
    """
    Runs a command with no output.

    :param command: The command to run.
    """

    subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE,
        stdin=subprocess.PIPE, stderr=subprocess.PIPE
    )
# end run_silent_command

def virtualenv_interpreter_location() -> str:
    """
    Returns the location of the interpreter in the venv.

    :return: The location of the interpreter.
    """

    return os.path.split(sys.executable)[0]
# end activate_virtualenv_command

def activate_virtualenv_command() -> str:
    """
    Returns the command to activate the virtual env.

    :return: The command to activate the venv.
    """

    python_startup = (
        virtualenv_interpreter_location() /
        Path('activate')
    )

    return (
        f"{'' if 'win' in sys.platform else 'source '}"
        f"{python_startup}"
    )
# end activate_virtualenv_command

def validate_requirement(
        name: str,
        path: Optional[str] = None,
        version: Optional[str] = None,
        quiet: Optional[bool] = True,
        silence: Optional[bool] = False
) -> None:
    """
    Installs the required package.

    :param name: The name of the package.
    :param path: The path to the package.
    :param version: The version to install.
    :param quiet: The value to show the installation process.
    :param silence: The value to silence.
    """

    if version is None:
        version = ""

    elif isinstance(version, str) and ("=" not in version):
        version = f"~{version}"

    else:
        version = ""
    # end if

    try:
        importlib.import_module(name)

    except ImportError:
        arguments = [
            'install',
            f'{(path if path is not None else name) + version}'
        ]

        if quiet:
            arguments.append("--quiet")
        # end if

        command = (
            f"{activate_virtualenv_command()} && "
            f"{Path(virtualenv_interpreter_location()) / Path('python')} -m pip "
            f"{' '.join(arguments)}"
        )

        if silence:
            with suppress():
                os.system(command)
            # end suppress

        else:
            os.system(command)
        # end if

        try:
            importlib.import_module(name)

        except ImportError:
            raise ImportError(f"{name} module is not found.")
        # end try
    # end try
# end validate_requirements

def documentation(module: str) -> Dict[str, str]:
    """
    Documents a module with its content objects documentation.

    :param module: The name of the module.

    :return: The documentation of the module.
    """

    documents = {
        f"{value.__module__}.{value.__name__}": value
        for name, value in sorted(
            list(sys.modules[module].__dict__.items()),
            key=lambda item: item[0]
        )
        if (
            hasattr(value, '__module__') and
            hasattr(value, '__name__') and
            hasattr(value, '__doc__') and
            hasattr(value, '__init__')
        )
    }

    return {
        key: f'`{key}`\n{value.__doc__}'
        for key, value in documents.items()
    }
# end documentation

def document(obj: Any) -> None:
    """
    Documents a module with its content objects documentation.

    :param obj: The obj to document.
    """

    obj.__doc__ += """\n\n""".join(
        documentation(obj.__module__).values()
    )
# end document