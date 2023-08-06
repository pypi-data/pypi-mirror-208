# pystatic

> This package is a collection of methods and classes for making python more secure, robust, and reliable.
> This could be achieved through the simple usage of decorators, function calls and inheritance of base classes.
> Generally, this package can make python a programming language, closer to other static-typed languages, 
> without losing python's dynamic powerful features and.

first of all
------------

#### specifics:

- writen and owned by: Shahaf Frank-Shapir
- all the rights are saved for: Shahaf Frank-Shapir
- program version: 0.0.0
- programming languages: python 3.9.12 (100%)

before we start
---------------

#### description:

> This package contains the following systems to be embedded in any python codebase:
> 
> - overloading: Functions and methods (static, class and instance) 
> can have the same name yet different arguments' signature 
> (different arguments - different names or same names and difference 
> in type hints.) through the usage of the overload decorator on top 
> of the base function\method and inherit from the overloading 
> protocol class, when the usage is made in a class.
>
> - privacy: Attributes of classes and instances can now be private 
> in a way that prevents getting access to them in the traditional 
> ways, as well as the more shady ones This can be used whn a class 
> inherits from the private property protocol, or the private attributes 
> being defined as private using the private descriptor.
>
> - cleaning: Cleaning of unnecessary objects, values, imported namespaces 
> from your modules, so an object imported into a module cannot be 
> imported with anything else that is written inside the module. 
> Essentially, enforcing what can and cannot be imported from you modules.
>
> - scope protection: The protection of attributes that are being accessed 
> from outside their class scope, so they couldn't be modified there.
>
> - automatic dynamic type checking and enforcement: decorators 
> and functions to check at run-time is the type, and structure of 
> types of the object equals to any type hint This can be done for 
> functions at every call for all the parameters, sing a decorator, 
> or manually, calling a function on a variable.

#### dependencies:

- opening:
  As for this is a really complex program, which uses a lot of modules, there are required dependencies needed
  in order to run the program. keep in mined the program was writen in python 3.9, so any python version lower
  than 3.8 might not work properly. Moreover, built-in python modules are being used, so keep that in mind.

- install app dependencies by writing the "-r" option to install the requirements
  writen in a file, and write the following line in the project directory:
````
pip install -r requirements.txt
````

run a test
-----------

#### run from windows command line (inside the project directory)
- run with python by writing to the command line in the project directory:
````
python test.py
````

- An example of the usage of runtime type-enforcement, private attributes and method overloading.
```python
import time
import warnings

from pystatic.overload import OverloadProtocol, overload
from pystatic.types import statictypes
from pystatic.private import private, PrivatePropertyProtocol
from pystatic.casting import Castable, cast

class Demo1(Castable):

  def __init__(self, a, b, c, x=None):

    self.a = a
    self.b = b
    self.c = c
    self.x = x

class Demo2(Castable):

  def __init__(self, a, b, c, x=None, y=None, z=None):

    self.a = a
    self.b = b
    self.c = c
    self.x = x
    self.y = y
    self.z = z

demo2 = Demo2(0, 1, 2, 3, 4, 5)
demo1 = cast(Demo1, demo2)

print(demo2, demo2.dict)
print(demo1, demo1.dict)

# noinspection PyNestedDecorators
class Foo(OverloadProtocol, PrivatePropertyProtocol):

    c = private()

    def __init__(self):

        print("\nclass Foo:\n\n\tdef __init__(self):\n")

        self.c = 1
        print("\t\t>>> self.c = 1")
        print("\t\t>>> print(self.c)")
        print(f"\t\t{self.c}\n")

        self.__d = 1
        print("\t\t>>> self.__d = 1")
        print("\t\t>>> print(self.__d)")
        print(f"\t\t{self.__d}\n")

        self.c = 0
        print("\t\t>>> self.c = 0")
        print("\t\t>>> print(self.c)")
        print(f"\t\t{self.c}\n")

        self.__d = 0
        print("\t\t>>> self.__d = 0")
        print("\t\t>>> print(self.__d)")
        print(f"\t\t{self.__d}\n")

    @overload
    def a(self, x: int):
        print("\n\tdef a(self, x: int):")
        print(f"\n\t\t>>> print(type(x))")
        print(f"\t\t{type(x)}\n")

    @a.overload
    @staticmethod
    def a(x: float):
        print("\n\t@staticmethod\n\tdef a(x: float):")
        print(f"\n\t\t>>> print(type(x))")
        print(f"\t\t{type(x)}\n")

    @a.overload
    @classmethod
    def a(cls, x: float):
        print("\n\t@classmethod\n\tdef a(cls, x: float):")
        print(f"\n\t\t>>> print(type(x))")
        print(f"\t\t{type(x)}\n")

    @statictypes(crush=False)
    def b(self, x: int):
        print("\n\t@statictypes(crush=False)\n\tdef b(self, x: int):")
        print(f"\n\t\t>>> print(type(x))")
        print(f"\t\t{type(x)}\n")

foo = Foo()

foo.a(0)
foo.a(0.0)

Foo.a(0)
Foo.a(0.0)

foo.b(0)
# noinspection PyTypeChecker
foo.b(0.0)

time.sleep(0.2)

try:
    print("\n>>> print(Foo.c)")
    print(Foo.c)

except AttributeError as e:
    warnings.warn(str(e))
# end try

time.sleep(0.2)

try:
    print("\n>>> print(foo.c)")
    print(foo.c)

except AttributeError as e:
    warnings.warn(str(e))
# end try

time.sleep(0.2)

try:
    print("\n>>> print(foo._Foo__d)")
    # noinspection PyProtectedMember
    print(foo._Foo__d)

except AttributeError as e:
    warnings.warn(str(e))
# end try

time.sleep(0.2)
```
- Output:
````python
<__main__.Demo2 object at 0x000001E16DB3F650> {'a': 0, 'b': 1, 'c': 2, 'x': 3, 'y': 4, 'z': 5}
<__main__.Demo1 object at 0x000001E16DB3F750> {'a': 0, 'b': 1, 'c': 2, 'x': 3, 'y': 4, 'z': 5}

class Foo:

        def __init__(self):

                >>> self.c = 1
                >>> print(self.c)
                1

                >>> self.__d = 1
                >>> print(self.__d)
                1

                >>> self.c = 0
                >>> print(self.c)
                0

                >>> self.__d = 0
                >>> print(self.__d)
                0


        def a(self, x: int):

                >>> print(type(x))
                <class 'int'>


        @staticmethod
        def a(x: float):

                >>> print(type(x))
                <class 'float'>


        def a(self, x: int):

                >>> print(type(x))
                <class 'int'>


        @staticmethod
        def a(x: float):

                >>> print(type(x))
                <class 'float'>


        @statictypes(crush=False)
        def b(self, x: int):

                >>> print(type(x))
                <class 'int'>

types.py:166: RuntimeTypeWarning: Unexpected type <class 'float'> was passed to x when calling <function Foo.b at 0x0000021974C54A40>, but should have been <class 'int'> instead.
        @statictypes(crush=False)
        def b(self, x: int):

                >>> print(type(x))
                <class 'float'>


>>> print(Foo.c)
test.py:85: UserWarning: object of type <class 'NoneType'> has no attribute 'c'

>>> print(foo.c)
test.py:95: UserWarning: object of type <class '__main__.Foo'> has no attribute 'c'

>>> print(foo._Foo__d)
test.py:106: UserWarning: object of type <class '__main__.Foo'> has no attribute '_Foo__d'
````