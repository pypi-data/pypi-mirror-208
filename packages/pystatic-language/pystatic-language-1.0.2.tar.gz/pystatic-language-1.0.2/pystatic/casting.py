# casting.py

from abc import ABCMeta
import inspect
from typing import (
    Type, Any, Callable, Tuple, Dict, Union, Optional
)
from functools import wraps
from collections import OrderedDict

import dill

__all__ = [
    "Configuration",
    "CastableMeta",
    "Castable",
    "cast",
    "copy",
    "deep_copy",
    "CastType",
    "castable"
]

class Configuration:
    """A class to wrap classes to record the configuration of the instances."""

    class Keys:
        """A class to contain the keys for the commands."""

        RECORD = "__record__"
        ARGS = "args"
        KWARGS = "kwargs"
        SELF = "self"
        INITIALIZERS = "initializers"
        INIT = "__saved_init__"
    # end Keys

    def __new__(cls, model: Type):
        """
        Defines the class attributes.

        :param model: The model to wrap.
        """

        model.__init__ = Configuration.construct(model.__init__)

        return model
    # end __new__

    @staticmethod
    def construct(constructor: Callable) -> Callable:
        """
        Wraps the constructor of the model class.

        :param constructor: The init method of the class.

        :return: The wrapped init method.
        """

        def get_parameters(*args: Any, **kwargs: Any) -> Dict[str, Union[Tuple, Dict[str, Any]]]:
            """
            Defines the class attributes to wrap the init method.

            :param args: Any positional arguments.
            :param kwargs: Any keyword arguments

            :returns: The model object.
            """

            signature = inspect.signature(constructor)

            parameters = {
                **dict(signature.bind(*args, **kwargs).arguments)
            }

            if Configuration.Keys.ARGS in parameters:
                parameters[Configuration.Keys.ARGS] = (
                    parameters[Configuration.Keys.ARGS][1:]
                    if len(parameters[Configuration.Keys.ARGS]) > 0 else tuple()
                )
            # end if

            parameters.pop(Configuration.Keys.SELF, None)

            initializers = OrderedDict(signature.parameters)

            for key in signature.parameters:
                if key not in parameters:
                    initializers[key] = None

                    continue

                else:
                    # noinspection PyUnresolvedReferences
                    initializers[key] = parameters[key]
                # end if
            # end ofr

            initializers.pop(Configuration.Keys.SELF, None)

            parameters = {
                Configuration.Keys.ARGS: (
                    parameters[Configuration.Keys.ARGS]
                    if (Configuration.Keys.ARGS in parameters) else ()
                ),
                Configuration.Keys.KWARGS: (
                    parameters[Configuration.Keys.KWARGS]
                    if (Configuration.Keys.KWARGS in parameters) else {}
                ),
                Configuration.Keys.INITIALIZERS: initializers
            }

            return parameters
        # end get_parameters

        @wraps(constructor)
        def __init__(*args: Any, **kwargs: Any) -> None:
            """
            Defines the class attributes to wrap the init method.

            :param args: Any positional arguments.
            :param kwargs: Any keyword arguments

            :returns: The model object.
            """

            constructor(*args, **kwargs)

            try:
                instance = args[0]

            except IndexError:
                raise ValueError(
                    f"constructor must be an __init__ method of a "
                    f"{Callable} class or subclass instance."
                )
            # end try

            parameters = get_parameters(*args, **kwargs)

            setattr(instance, Configuration.Keys.INIT, constructor)
            setattr(instance, Configuration.Keys.RECORD, parameters)
        # end __init__

        return __init__
    # end construct
# end Configuration

class CastableMeta(ABCMeta):
    """A class to represent a castable meta class."""

    def __init__(cls, name: str, bases: Tuple, attr_dict: Dict[str, Any]) -> None:
        """
        Defines the class attributes.

        :param name: The type name.
        :param bases: The valid_bases of the type.
        :param attr_dict: The attributes of the type.
        """

        super().__init__(name, bases, attr_dict)

        cls.__init__ = Configuration.construct(cls.__init__)
    # end __init__
# end CastableMeta

class Castable(metaclass=CastableMeta):
    """A class to represent a castable class."""

    @property
    def dict(self) -> Dict[str, Any]:
        """
        Returns the dict of the object data.

        :return: The data of the object.
        """

        data = self.__dict__.copy()

        data.pop(Configuration.Keys.INIT, None)
        data.pop(Configuration.Keys.RECORD, None)

        return data
    # end dict
# end Castable

class CastType:
    """A class to represent a casting type mechanism."""

    def __init__(self, base: Type) -> None:
        """
        Defines the class attributes.

        :param base: The type to cast the object into.
        """

        self.base = base
    # end __init__

    def __call__(self, instance: object, init: Optional[bool] = False) -> Castable:
        """
        Creates a casting mechanism for casting objects into different types.

        :param instance: The object instance to cast into the new type.
        :param init: The value to call the init function.

        :return: The new object of the new type.
        """

        signature = inspect.signature(self.base.__init__)

        try:
            if init and isinstance(instance, Castable):
                parameters = dict(
                    {
                        key: value for key, value in
                        instance.__record['initializers'].items()
                        if key in signature.parameters
                    }
                )

                new_instance = self.base(**parameters)

            else:
                base: Type[Castable]

                # noinspection PyArgumentList
                new_instance = self.base.__new__(self.base)
            # end if

            new_instance.__dict__.update(
                {
                    key: value for key, value in instance.dict.items()
                    if key in signature.parameters
                }
            )

            return new_instance

        except (ValueError, TypeError) as e:
            raise TypeError(
                f"Cannot cast {repr(instance)} into "
                f"{repr(self.base)}. {str(e)}"
            )
        # end try
    # end __call__
# end CastType

def castable(base: Type) -> CastType:
    """
    Creates a casting mechanism for casting objects into different types.

    :param base: The type to cast the object into.

    :return: The new object of the new type.
    """

    return CastType(base=base)
# end castable

def cast(base: Type, instance: object, init: Optional[bool] = False) -> Castable:
    """
    Creates a casting mechanism for casting objects into different types.

    :param base: The type to cast the object into.
    :param instance: The object instance to cast into the new type.
    :param init: The value to call the init function.

    :return: The new object of the new type.
    """

    return castable(base=base)(instance=instance, init=init)
# end cast

def copy(instance: Any, init: Optional[bool] = False) -> Any:
    """
    Creates a copy mechanism for copying objects.

    :param instance: The object instance to copy.
    :param init: The value to call the init function.

    :return: The new object copy.
    """

    return cast(type(instance), instance=instance, init=init)
# end copy

def deep_copy(instance: Any) -> Any:
    """
    Creates a deep copy mechanism for copying objects.

    :param instance: The object instance to copy.

    :return: The new object copy.
    """

    return dill.loads(dill.dumps(instance))
# end deep_copy