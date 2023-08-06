import inspect
from typing import Any, Optional


def get_ipython_string() -> Optional[str]:
    """
    :return: "ZMQInteractiveShell" for jupyter notebook, "TerminalInteractiveShell" for ipython in terminal, None otherwise.
    """
    try:
        # I know this has a redline under it... we'll catch the NameError as a Falsy condition below
        # noinspection PyUnresolvedReferences
        shell = get_ipython().__class__.__name__
        return shell
    except NameError:
        return None  # Probably standard Python interpreter


def is_notebook() -> bool:
    """:return: true if run inside a Jupyter notebook"""
    shell = get_ipython_string()
    return shell == "ZMQInteractiveShell"


def is_defined_in_module(obj: Any) -> bool:
    """
    Whether the given object was defined in a module that was imported, or if it's defined at the top level of a shell/script.
    :return: True if object was defined inside a module.
    """
    m = inspect.getmodule(obj)
    return m.__name__ != "__main__"
