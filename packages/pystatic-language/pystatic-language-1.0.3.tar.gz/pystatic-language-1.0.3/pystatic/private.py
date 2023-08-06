# private.py

import inspect
from typing import Any, Optional

__all__ = [
    "PrivateProperty",
    "GeneralPrivateProtocol",
    "PrivatePropertyProtocol",
    "private"
]

def error_message(obj: Any, name: str) -> str:
    """
    Defines the class attributes.

    :param obj: The object to wrap.
    :param name: The attribute's name.
    """

    if inspect.isclass(obj):
        base = ''

    else:
        obj = type(obj)
        base = 'object of type '
    # end if

    return f"{base}{repr(obj)} has no attribute '{name}'"
# end type_error_message

def in_scope(obj: Any, levels: Optional[int] = 2) -> Any:
    """
    Checks if the statement is inside the scope of the object class.

    :param obj: The instance of the class.
    :param levels: The amount of levels to search in.

    :return: A boolean flag.
    """

    frame = inspect.currentframe()

    for _ in range(levels):
        if hasattr(frame, "f_back") and frame.f_back is not None:
            frame = frame.f_back

        else:
            break
        # end if
    # end for

    return list(frame.f_locals.values())[0] is obj
# end in_scope

class PrivateProperty:
    """A descriptor for private attributes."""

    def __init__(self, value: Optional[Any] = None) -> None:
        """
        Sets the private value.

        :param value: The value to store.
        """

        self.instance: Optional[Any] = None

        self.value = value
    # end __init__

    def __set_name__(self, instance: Any, name: str) -> None:
        """
        Sets the name of the attribute in the class.

        :param instance: The attribute owner as the class.
        :param name: The name of the attribute.
        """

        self.instance = instance

        self.name = name
    # end __set_name__

    def __get__(self, instance: Any, owner: Any) -> Any:
        """
        Gets the attribute value.

        :param instance: The instance of the class.
        :param owner: The class type of the instance.

        :return: The attribute's value.
        """

        self.instance = instance or self.instance

        if not in_scope(self.instance, levels=4):
            raise AttributeError(
                error_message(self.instance, self.name)
            )

        else:
            return self.value
        # end if
    # end __get__

    def __set__(self, instance: Any, value: Any) -> None:
        """
        Sets the attribute value.

        :param instance: The instance of the class.
        :param value: The attribute's value.
        """

        if not in_scope(instance):
            raise AttributeError(
                error_message(self.instance, self.name)
            )

        else:
            self.value = value
        # end if
    # end __set__
# end PrivateProperty

class GeneralPrivateProtocol:
    """A base model class to be the base of all objects."""

    def __getattribute__(self, key: str) -> Any:
        """
        Gets the attribute value.

        :param key: The name of the attribute.

        :return: The attribute value.
        """

        inside = in_scope(self)

        if (
            (key.startswith(f"_{type(self).__name__}__") and (not inside)) or
            hasattr(type(self), key)
        ):
            raise AttributeError(error_message(self, key))

        else:
            return super().__getattribute__(key)
        # end if
    # end __getattribute__

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Sets the attribute value.

        :param key: The name of the attribute.
        :param value: The attribute's value.
        """

        if key in dir(object):
            return super().__setattr__(key, value)
        # end if

        if in_scope(self):
            return super().__setattr__(key, value)

        else:
            raise AttributeError(error_message(self, key))
        # end if
    # end __setattr__
# end GeneralPrivateProtocol

class PrivatePropertyProtocol:
    """A base model class to be the base of all objects."""

    def __getattribute__(self, key: str) -> Any:
        """
        Gets the attribute value.

        :param key: The name of the attribute.

        :return: The attribute value.
        """

        if key in dir(object):
            return super().__getattribute__(key)
        # end if

        inside = in_scope(self, levels=3)

        if (
            (key.startswith(f"_{type(self).__name__}__") and not inside) or
            (
                not inside and not hasattr(self, key) and
                not key.startswith(f"_{type(self).__name__}__")
            )
        ):
            raise AttributeError(error_message(self, key))

        else:
            return super().__getattribute__(key)
        # end if
    # end __getattribute__

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Sets the attribute value.

        :param key: The name of the attribute.
        :param value: The attribute's value.
        """

        if key in dir(object):
            return super().__setattr__(key, value)
        # end if

        inside = in_scope(self)

        if (
            (key.startswith(f"_{type(self).__name__}__") and not inside) or
            (
                not inside and not hasattr(self, key) and
                not key.startswith(f"_{type(self).__name__}__")
            )
        ):
            raise AttributeError(error_message(self, key))

        else:
            super().__setattr__(key, value)
        # end if
    # end __setattr__
# end PrivatePropertyProtocol

private = PrivateProperty