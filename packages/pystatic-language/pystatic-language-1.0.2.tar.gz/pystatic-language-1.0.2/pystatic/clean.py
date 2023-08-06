# clean.py

from typing import Iterable, Optional

__all__ = [
    "clean_module"
]

def clean_module(name: str, properties: Optional[Iterable[str]] = None) -> None:
    """
    Cleans the module properties from attributes that are not in the __all__ list.

    :param properties: The properties to save.
    :param name: The name of the module.
    """

    import sys

    module = sys.modules[__name__]

    if properties is None:
        properties = [
            key for key, value in module.__dict__.items()
            if (
                (hasattr(value, '__module__')) and
                (value.__module__ == name)
            )
        ]

    elif not isinstance(properties, list):
        properties = list(properties)
    # end if

    definitions = [
        "__name__",
        "__doc__",
        "__package__",
        "__loader__",
        "__spec__",
        "__all__",
        "__file__",
        "__cached__",
        "__builtins__",
        "__annotations__"
    ]

    for key in sys.modules[name].__dict__.copy():
        if (
            (key not in properties + definitions) and
            (key in sys.modules[name].__dict__)
        ):
            sys.modules[name].__dict__.pop(key)
        # end if
    # end for
# end clean_module