# types.py

from abc import ABCMeta
import inspect
import warnings
from typing import (
    Any, Union, Optional, Callable, Type, Sequence
)

from typeguard import check_type

__all__ = [
    "Config",
    "RuntimeTypeWarning",
    "RuntimeTypeError",
    "validate",
    "statictypes",
    "typecheck"
]

class Config(metaclass=ABCMeta):
    """A class for config settings and system control."""

    enforce = True
    crush = True
# end Config

def type_error_message(
        obj: Union[Type, Callable], name: str, incorrect: Any, correct: Any
) -> str:
    """
    Returns the error message.

    :param obj: The object to wrap.
    :param name: The attribute's name.
    :param incorrect: The incorrect value.
    :param correct: The correct value.
    """
    
    return (
        f"Unexpected type {incorrect} was passed to {name} "
        f"when calling {obj}, but should have been {correct} instead."
    )
# end type_error_message

class RuntimeTypeError(TypeError):
    """A class to represent a runtime type error."""

    def __init__(
            self,
            obj: Union[Type, Callable],
            name: str,
            incorrect: Any,
            correct: Any
    ) -> None:
        """
        Defines the class attributes.

        :param obj: The object to wrap.
        :param name: The attribute's name.
        :param incorrect: The incorrect value.
        :param correct: The correct value.
        """

        super().__init__(
            type_error_message(
                obj=obj, name=name, incorrect=incorrect,
                correct=correct
            )
        )
    # end __init__
# end RuntimeValueTypeError

class RuntimeTypeWarning(Warning):
    """A class to represent a runtime type warning."""
# end RuntimeTypeWarning

def __validate(
        obj: Optional[Union[Type, Callable]] = None, *,
        excluded_names: Optional[Sequence[str]] = None,
        excluded_hints: Optional[Sequence[Any]] = None,
        crush: Optional[bool] = None
) -> Union[Callable[..., Any], Callable[[Union[Type, Callable]], Callable[..., Any]]]:
    """
    Wraps a callable object with runtime type enforcement.

    :param obj: The callable object.
    :param excluded_names: The names to exclude from the check.
    :param excluded_hints: The hints to exclude from the check.
    ude from the check.
    

    :returns: The inner wrapper function.
    """

    if crush is None:
        crush = Config.crush
    # end if

    excluded_names = excluded_names or ()
    excluded_hints = excluded_hints or ()

    def wrap_call(*args: Any, **kwargs: Any) -> Any:
        """
        Wraps a callable object with runtime type enforcement.

        :param args: Any positional argument.
        :param kwargs: Any keyword argument.

        :returns: The returned value.
        """

        signature = inspect.signature(obj)

        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        parameters = dict(zip(signature.parameters, bound.args))
        parameters.update(bound.kwargs)

        for key, value in obj.__annotations__.items():
            if any(
                [
                    (key == "return"),
                    (key in excluded_names),
                    (value in excluded_hints)
                ]
            ):
                continue
            # end if
            
            try:
                check_type(key, parameters[key], value)
            
            except TypeError:
                if crush:
                    raise RuntimeTypeError(
                        obj=obj, name=key, correct=value,
                        incorrect=type(parameters[key])
                    )
                
                else:
                    warnings.warn(
                        type_error_message(
                            obj=obj, name=key, correct=value,
                            incorrect=type(parameters[key])
                        ), RuntimeTypeWarning
                    )
                # end if
            # end try
        # end for

        data = obj(*args, **kwargs)

        key = 'return'

        if (key in obj.__annotations__) and (key not in excluded_names):
            try:
                check_type(key, data, obj.__annotations__[key])
            
            except TypeError:
                if crush:
                    raise RuntimeTypeError(
                        obj=obj, name=key, incorrect=type(data),
                        correct=obj.__annotations__[key]
                    )
                
                else:
                    warnings.warn(
                        type_error_message(
                            obj=obj, name=key, incorrect=type(data),
                            correct=obj.__annotations__[key]
                        ), RuntimeTypeWarning
                    )
                # end if
            # end try
        # end if

        return data
    # end wrap_call

    if obj is not None:
        return wrap_call
    
    else:
        def wrap_wrapper(value: Union[Type, Callable]) -> Callable:
            """
            Wraps a callable object with runtime type enforcement.

            :param value: The callable object.

            :returns: The inner wrapper function.
            """

            nonlocal obj

            obj = value

            return wrap_call
        # end wrap_wrapper

        return wrap_wrapper
    # end if
# end __validate

def validate(
        obj: Optional[Union[Type, Callable]] = None, *,
        excluded_names: Optional[Sequence[str]] = None,
        excluded_hints: Optional[Sequence[Any]] = None,
        crush: Optional[bool] = None
) -> Union[Callable[..., Any], Callable[[Union[Any, Type, Callable]], Callable[..., Any]]]:
    """
    Wraps a callable object with runtime type enforcement.

    :param obj: The callable object.
    :param excluded_names: The names to exclude from the check.
    :param excluded_hints: The hints to exclude from the check.
    :param crush: The value to raise errors.

    :returns: The inner wrapper function.
    """

    if not Config.enforce:
        return obj
    # end if

    if inspect.isclass(obj):
        for key in dir(obj):
            if key.startswith("_") or not callable(getattr(obj, key)):
                continue
            # end if

            setattr(
                obj, key, __validate(
                    getattr(obj, key), excluded_names=excluded_names, 
                    excluded_hints=excluded_hints, crush=crush
                )
            )
        # end for

        return obj

    else:
        return __validate(
            obj, excluded_names=excluded_names, 
            excluded_hints=excluded_hints, crush=crush
        )
    # end if
# end validate

def typecheck(
        value: Any,
        hint: Any,
        name: Optional[str] = None,
        crush: Optional[bool] = True
) -> bool:
    """
    Checks the type of variable by its type hinting.

    :param value: The object to check.
    :param hint: The type hinting.
    :param name: The name of the variable.
    :param crush: The value to raise errors.

    :return: The validation's value.
    """

    name = name or "variable"

    try:
        check_type(name, hint, value)

        return True

    except TypeError:
        if crush:
            raise RuntimeTypeError(
                obj=value, name=name, incorrect=type(value),
                correct=hint
            )

        else:
            warnings.warn(
                type_error_message(
                    obj=value, name=name, incorrect=type(value),
                    correct=hint
                ), RuntimeTypeWarning
            )
        # end if
    # end try
# end typecheck

statictypes = validate