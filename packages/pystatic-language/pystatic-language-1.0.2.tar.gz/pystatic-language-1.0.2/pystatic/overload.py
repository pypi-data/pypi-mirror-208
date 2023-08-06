# overload.py

import inspect
from functools import partial
from typing import Callable, Any, Union, Tuple, Dict

from pystatic.types import (
    statictypes, RuntimeTypeError, RuntimeTypeWarning
)

__all__ = [
    "Overload",
    "OverloadProtocol",
    "overload"
]

def overload_signature_error_message(
        c: Callable, args: Tuple, kwargs: Dict[str, Any]
) -> str:
    """
    Returns the error message.

    :param c: The callable object.
    :param args: The arguments fof the call.
    :param kwargs: The keyword arguments for the call.

    :return: The error message.
    """

    return (
        f"No matching function signature found "
        f"from the overloading of {c} for the arguments: {args}, {kwargs}."
    )
# end overload_signature_error_message

class OverloadSignatureTypeError(TypeError):
    """A class to represent a runtime type error."""

    def __init__(
            self, c: Callable, args: Tuple, kwargs: Dict[str, Any]
    ) -> None:
        """
        Defines the class attributes.

        :param c: The callable object.
    :param args: The arguments fof the call.
    :param kwargs: The keyword arguments for the call.
        """

        super().__init__(
            overload_signature_error_message(
                c=c, args=args, kwargs=kwargs
            )
        )
    # end __init__
# end OverloadSignatureTypeError

class OverloadSignatureTypeWarning(Warning):
    """A class to represent a runtime type warning."""
# end OverloadSignatureTypeWarning

def is_regular_method(method: Union[Callable, staticmethod, classmethod]) -> bool:
    """
    Checks if the method is not static or class method.

    :returns: The boolean value.
    """

    return not isinstance(method, (staticmethod, classmethod))
# end is_regular_method

def get_callable_method(method: Union[Callable, staticmethod, classmethod]) -> Callable:
    """
    Gets the callable method from the given method.

    :returns: The callable method.
    """

    return method if is_regular_method(method) else method.__func__
# end get_callable_method

class OverloadProtocol:
    """A class to enable the overload inside classes."""

    def __getattribute__(self, key: str) -> Any:
        """
        Gets the attribute value.

        :param key: The name of the attribute.

        :return: The attribute value.
        """

        val = super().__getattribute__(key)

        if isinstance(val, Overload):
            val.instance = self
        # end if

        return val
    # end __getattribute__
# end OverloadProtocol

class Overload:
    """A class to create an overload functionality."""

    def __init__(self, c: Callable) -> None:
        """
        Defines the class attributes.

        :param c: The decorated callable object.
        """

        self.instance = None

        self.c = c

        self.signatures: Dict[
            inspect.Signature,
            Union[Callable, classmethod, staticmethod]
        ] = {}
    # end __init__

    def overload(self, c: Callable) -> object:
        """
        sets the signature of the decorated overloading callable object in the class.

        :param c: The decorated callable object.

        :return: The current class object.
        """

        self.signatures[inspect.signature(get_callable_method(c))] = c

        return self
    # end overload

    # noinspection PyUnresolvedReferences
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Calls the decorated callable with the overloading match.

        :param args: The positional arguments.
        :param kwargs: The keyword arguments.

        :return: The returned value from the callable call.
        """

        for signature, c in self.signatures.items():
            try:
                if isinstance(c, staticmethod):
                    c = c.__func__

                elif self.instance is not None:
                    if isinstance(c, classmethod):
                        annotations = c.__func__.__annotations__
                        c = partial(c, type(self.instance))
                        c.__annotations__ = annotations

                    else:
                        annotations = c.__annotations__
                        c = partial(c, self.instance)
                        c.__annotations__ = annotations
                    # end if
                # end if

                return statictypes(c)(*args, **kwargs)

            except (RuntimeTypeError, RuntimeTypeWarning, TypeError):
                pass
            # end try
        # end for

        c = self.c

        if isinstance(c, staticmethod):
            c = c.__func__

        elif self.instance is not None:
            if isinstance(c, classmethod):
                annotations = c.__func__.__annotations__
                c = partial(c, type(self.instance))
                c.__annotations__ = annotations

            else:
                annotations = c.__annotations__
                c = partial(c, self.instance)
                c.__annotations__ = annotations
            # end if
        # end if

        try:
            return statictypes(c)(*args, **kwargs)

        except (RuntimeTypeError, TypeError):
            raise OverloadSignatureTypeError(
                c=self.c, args=args, kwargs=kwargs
            )

        except RuntimeTypeWarning:
            warnings.warn(
                overload_signature_error_message(
                    c=self.c, args=args, kwargs=kwargs
                ), OverloadSignatureTypeWarning
            )
        # end try
    # end __call__
# end Overload

overload = Overload