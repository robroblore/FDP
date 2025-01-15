# coding=utf-8
import timeit
import unittest
from abc import get_cache_token, ABC, abstractmethod
from functools import update_wrapper
from inspect import signature, Parameter
from types import MappingProxyType
from typing import get_args, get_type_hints, Any, Union


class MultiDispatchError(Exception):
    """Exception raised for multi-dispatch related errors."""


def is_union_type(cls):
    return getattr(cls, "__origin__", None) is Union


def is_valid_dispatch_type(cls):
    if isinstance(cls, type):
        return True
    return (
        is_union_type(cls)
        and all(isinstance(arg, type) for arg in get_args(cls))
    )


def is_optional(key: str, param: (type, Any)):
    return param[1] != Parameter.empty or key[0] == "*"


def is_annotation_compatible(arg: type, param: (type, Any)):
    if (
        arg is param
        or issubclass(arg, param)
        or arg in get_args(param)
        or param is Any
    ):
        return True
    return False


def MultiDispatch(*defaultTypes: Any, default_func: Any = None, selfParam: str = "self"):
    """
    Multiple-dispatch generic function decorator.

    Transforms a function into a generic function, which can have different
    behaviors depending upon the type of its arguments. The decorated
    function acts as the default implementation, and additional
    implementations can be registered using the register() attribute of the
    generic function.
    """

    """
    Initialize the MultiDispatch decorator.

    :param *types: Variable-length argument list of dispatch types.
    :param func: The function being decorated.
    :param selfParam: The name of the self parameter.
    """
    registry = {}
    dispatch_cache = {}
    cache_token = None
    default_func = default_func

    def get_matching_signature(args: tuple, kwargs: dict):
        for func, params in reversed(registry.items()):
            params: dict = params.copy()
            if is_types_compatible(params, args):
                if is_params_compatible(params, kwargs):
                    if all(is_optional(param, params[param]) for param in params):
                        return func
        return None

    def is_types_compatible(params: dict, args: tuple):
        keys = list(params.keys())
        values = list(params.values())
        i = 0
        for index, arg in enumerate(args):
            if len(keys) > index and keys[i][0] != "*":
                i += 1
                if is_annotation_compatible(arg, values[index][0]):
                    params.pop(keys[index])
                else:
                    return False
            elif len(keys) <= i or not (
                keys[i][0] == "*"
                and keys[i][1] != "*"
                and is_annotation_compatible(arg, values[i][0])
            ):
                return False
        if len(keys) > i and keys[i][0] == "*" and keys[i][1] != "*":
            params.pop(keys[i])
        return True

    def is_params_compatible(params: dict, kwargs: dict):
        keys = list(params.keys())
        i = 0
        for index, key in enumerate(kwargs.keys()):
            if len(keys) > index and keys[i][:2] != "**":
                i += 1
                if (
                    key in keys
                    and is_annotation_compatible(type(kwargs[key]), params[key][0])
                ):
                    params.pop(key)
                else:
                    return False
            elif len(keys) == 0 or not (
                keys[-1][:2] == "**"
                and is_annotation_compatible(type(kwargs[key]), params[keys[i]][0])
            ):
                return False
        return True

    def dispatch(*args, **kwargs):

        nonlocal cache_token
        arg_types = tuple(type(arg) for arg in args)
        kwargs_cache = tuple((key, type(kwargs[key])) for key in kwargs)

        if cache_token:
            current_token = get_cache_token()
            if cache_token != current_token:
                dispatch_cache.clear()
                cache_token = current_token
        try:
            impl = dispatch_cache[(arg_types, kwargs_cache)]
        except KeyError:
            impl = get_matching_signature(arg_types, kwargs)
            dispatch_cache[(arg_types, kwargs_cache)] = impl

        if impl:
            return impl
        else:
            params = ", ".join(
                f"{param}={kwargs[param]}"
                for index, param in enumerate(kwargs)
            )

            signatures = "\t"
            for i, func in enumerate(registry):
                s = ", ".join(
                    f"{param}: {registry[func][param][0]}"
                    + (
                        f" = {registry[func][param][1]}"
                        if registry[func][param][1] != Parameter.empty
                        else ""
                    )
                    for param in registry[func]
                )
                signatures += f"{default_func.__name__}({s})"
                if i != len(registry) - 1:
                    signatures += ", \n \t"
            raise MultiDispatchError(
                f"No implementation found for {default_func.__name__}({', '.join(map(repr, args))}{', ' if len(args) > 0 and len(params) > 0 else ''}{params})\n"
                f"among stored signatures: \n"
                f"{signatures}"
            )

    def register(*types: Any, func: Any = None, selfParam: str = "self") -> Any:
        """
        Register an implementation for the given combination of types.

        :param types: Variable-length argument list of dispatch types.
        :param func: The function implementation.
        :param selfParam: The name of the self parameter.

        :return: The registered function.
        """
        nonlocal default_func
        nonlocal cache_token

        if not func:
            if not all(is_valid_dispatch_type(arg) for arg in types):
                if len(types) > 1:
                    for arg in types:
                        if not is_valid_dispatch_type(arg):
                            if is_union_type(arg):
                                raise TypeError(f"{arg!r} not all arguments are modules, classes, methods, or functions.")
                            else:
                                raise TypeError(f"{arg!r} is not a module, class, method, or function.")
                return register(func=types[0])
            return lambda f: register(*types, func=f)

        # Register the function implementation
        param_types = {}
        annotations = get_type_hints(func)
        parameters = list(signature(func).parameters.values())
        if len(parameters) > 0 and "." in func.__qualname__ and parameters[0].name == selfParam:
            parameters.pop(0)

        for index, param in enumerate(parameters):
            default = param.default

            if param.kind is param.VAR_POSITIONAL:
                param = f"*{param.name}"
            elif param.kind is param.VAR_KEYWORD:
                param = f"**{param.name}"
            else:
                param = param.name

            if len(types) > index:
                param_types[param] = (types[index], default)
            elif param in annotations:
                param_types[param] = (annotations[param], default)
            elif param[:2] == "**" and param[2:] in annotations:
                param_types[param] = (annotations[param[2:]], default)
            elif param[0] == "*" and param[1:] in annotations:
                param_types[param] = (annotations[param[1:]], default)
            else:
                param_types[param] = (Any, default)

        # Check if the function has already been registered
        for entry in registry:
            if registry[entry] == param_types and entry == func:
                s = ", ".join(
                    f"{param}: {param_types[param][0]}"
                    + (f" = {param_types[param][1]}"
                       if param_types[param][1] != Parameter.empty else "")
                    for param in param_types
                )
                signatures = f"{default_func.__name__}({s})"
                raise MultiDispatchError(
                    "Function already registered for the given types.\n"
                    f"{signatures}"
                )
        registry[func] = param_types

        if not default_func:
            update_wrapper(wrapper, func)
            default_func = func

        if not cache_token and hasattr(func, '__abstractmethods__'):
            cache_token = get_cache_token()

        dispatch_cache.clear()

        return func

    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f'{funcname} requires at least '
                            '1 positional argument')

        return dispatch(args[0].__class__)(*args, **kw)

    funcname = getattr(default_func, '__name__', 'singledispatch function')
    register(*defaultTypes, func=default_func, selfParam=selfParam)
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.defaultTypes = defaultTypes
    wrapper.registry = MappingProxyType(registry)
    wrapper._clear_cache = dispatch_cache.clear
    update_wrapper(wrapper, default_func)
    return wrapper


class Overload:
    """
    Overload generic method descriptor.

    Supports wrapping existing descriptors and handles non-descriptor
    callables as instance methods.
    """

    def __init__(self, *types: Any, func: Any = None, selfParam: str = "self"):
        """
        Initialize the MultiDispatch decorator.

        :param *types: Variable-length argument list of dispatch types.
        :param func: The function being decorated.
        :param selfPram: The name of the self parameter.
        """
        if not func:
            if not all(is_valid_dispatch_type(arg) for arg in types):
                func = types[0]
                types = types[1:]
        self.dispatcher = MultiDispatch(*types, default_func=func, selfParam=selfParam)
        self.func = func

    def register(self, *types: Any, func: Any = None, selfParam: str = "self") -> Any:
        """
        Register an implementation for the given combination of types.

        :param types: Variable-length argument list of dispatch types.
        :param func: The function implementation.
        :param selfPram: The name of the self parameter.

        :return: The registered function.
        """
        return self.dispatcher.register(*types, func=func, selfParam=selfParam)

    def __get__(self, obj, cls=None):
        def _method(*args, **kwargs):
            method = self.dispatcher.dispatch(*args, **kwargs)
            return method.__get__(obj, cls)(*args, **kwargs)

        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method.register = self.register
        update_wrapper(_method, self.func)
        return _method

    def __call__(self, *args, **kwargs):
        if self.func:
            method = self.dispatcher.dispatch(*args, **kwargs)
            return method.__call__(*args, **kwargs)
        else:
            self.func = args[0]
            self.dispatcher.register(*self.dispatcher.defaultTypes, func=self.func)
            return self

    @property
    def __isabstractmethod__(self):
        return getattr(self.func, '__isabstractmethod__', False)

    @__isabstractmethod__.setter
    def __isabstractmethod__(self, value):
        self.func.__isabstractmethod__ = value


class TestMultiDispatch(unittest.TestCase):

    def test_multiple_dispatch(self):
        @Overload
        def foo(x):
            return "object"

        @foo.register(int)
        def _(x):
            return "int"

        @foo.register(float)
        def _(x):
            return "float"

        self.assertEqual(foo(10), "int")
        self.assertEqual(foo(10.5), "float")
        self.assertEqual(foo("text"), "object")  # test_default_implementation
        with self.assertRaises(MultiDispatchError):  # test_missing_implementation
            foo("text", ["list"])

    def test_inheritance(self):
        class BaseClass:
            @Overload(int)
            def foo(self, x):
                return "BaseClass int"

        class SubClass(BaseClass):
            @BaseClass.foo.register(float)
            def _(self, x):
                return "SubClass float"

        obj = SubClass()
        self.assertEqual(obj.foo(10), "BaseClass int")
        self.assertEqual(obj.foo(10.5), "SubClass float")

    def test_abstract_methods(self):
        class BaseClassA(ABC):
            @abstractmethod
            @Overload
            def foo(x):
                return "BaseClass int"

        class BaseClassB(ABC):
            @staticmethod
            @abstractmethod
            def foo(x):
                return "BaseClass int"

        class SubClassA(BaseClassA):
            pass

        class SubClassB(BaseClassB):
            pass

        with self.assertRaises(TypeError):
            SubClassA()
        with self.assertRaises(TypeError):
            SubClassB()

    def test_optional_parameters(self):
        @Overload(int, str)
        def foo(x, y="default"):
            return f"int: {x}, str: {y}"

        @foo.register(int, int)
        def _(x, y):
            return f"int: {x}, int: {y}"

        self.assertEqual(foo(10), "int: 10, str: default")
        self.assertEqual(foo(10, "text"), "int: 10, str: text")
        self.assertEqual(foo(10, y="custom"), "int: 10, str: custom")
        self.assertEqual(foo(10, 20), "int: 10, int: 20")

    def test_multiple_parameters(self):
        @Overload(str, int)
        def foo(x, y):
            return f"str: {x}, int: {y}"

        @foo.register(str, float)
        def _(x, y):
            return f"str: {x}, float: {y}"

        @foo.register(str, int, int)
        def _(x, y, z):
            return f"str: {x}, int: {y}, int: {z}"

        @foo.register(int, float, int)
        def _(x, y, z):
            return f"int: {x}, float: {y}, int: {z}"

        self.assertEqual(foo("text", 10), "str: text, int: 10")
        self.assertEqual(foo("text", 10.5), "str: text, float: 10.5")
        self.assertEqual(foo("text", 10, 20), "str: text, int: 10, int: 20")
        self.assertEqual(foo(10, 10.5, 20), "int: 10, float: 10.5, int: 20")

    def test_parameters_type_hints(self):
        @Overload
        def foo(x: str, y: int):
            return f"str: {x}, int: {y}"

        @foo.register
        def _(x: str, y: float):
            return f"str: {x}, float: {y}"

        @foo.register
        def _(x: str, y: int, z: int):
            return f"str: {x}, int: {y}, int: {z}"

        @foo.register
        def _(x: int, y: float, z: int):
            return f"int: {x}, float: {y}, int: {z}"

        self.assertEqual(foo("text", 10), "str: text, int: 10")
        self.assertEqual(foo("text", 10.5), "str: text, float: 10.5")
        self.assertEqual(foo("text", 10, 20), "str: text, int: 10, int: 20")
        self.assertEqual(foo(10, 10.5, 20), "int: 10, float: 10.5, int: 20")

    def test_multiple_parameters_type_hints(self):
        @Overload
        def foo(*x: str):
            return f"{len(x)} str: {x}"

        @foo.register
        def _(**x: int):
            return f"{len(x)} int: {x}"

        @foo.register
        def _(x: int, *y: int):
            return f"int: {x}, {len(y)} int: {y}"

        @foo.register
        def _(x: str, **y: str):
            return f"str: {x}, {len(y)} str: {y}"

        @foo.register
        def _(x: str, *y: int, z: int):
            return f"str: {x}, {len(y)} int: {y}, int: {z}"

        @foo.register
        def _(x: str, *y: int, z: str, **a: int):
            return f"str: {x}, {len(y)} int: {y}, str: {z}, {len(a)} int: {a}"

        self.assertEqual(foo("text", "text", "text"), "3 str: ('text', 'text', 'text')")
        self.assertEqual(foo(x=10, y=20, z=30), "3 int: {'x': 10, 'y': 20, 'z': 30}")
        self.assertEqual(foo(10, 20, 30), "int: 10, 2 int: (20, 30)")
        self.assertEqual(foo(x="text", y="text", z="text"), "str: text, 2 str: {'y': 'text', 'z': 'text'}")
        self.assertEqual(foo("text", 10, 20, z=30), "str: text, 2 int: (10, 20), int: 30")
        self.assertEqual(foo("text", 10, 20, z="30", a=40, b=50, c=60), "str: text, 2 int: (10, 20), str: 30, 3 int: {'a': 40, 'b': 50, 'c': 60}")

    def test_unsupported_type(self):
        @Overload(int)
        def foo(x):
            return "int"

        with self.assertRaises(TypeError):
            @foo.register(int, "param")
            def _(x, y):
                return "int, int"

    def test_callable_object(self):
        class CallableClass:
            def __call__(self, x):
                return f"CallableClass: {x}"

        callable_obj = CallableClass()

        @Overload(CallableClass)
        def foo(x):
            return "CallableClass"

        self.assertEqual(foo(callable_obj), "CallableClass")
        self.assertEqual(callable_obj(10), "CallableClass: 10")

    def test_performance_test(self):
        @Overload
        def foo():
            return f"default"

        @foo.register
        def _(*x: str):
            return f"{len(x)} str: {x}"

        @foo.register
        def _(**x: int):
            return f"{len(x)} int: {x}"

        @foo.register
        def _(x: int, *y: int):
            return f"int: {x}, {len(y)} int: {y}"

        @foo.register
        def _(x: str, **y: str):
            return f"str: {x}, {len(y)} str: {y}"

        @foo.register
        def _(x: str, *y: int, z: int):
            return f"str: {x}, {len(y)} int: {y}, int: {z}"

        @foo.register
        def _(x: str, *y: int, z: str, **a: int):
            return f"str: {x}, {len(y)} int: {y}, str: {z}, {len(a)} int: {a}"

        @foo.register
        def _(x: int):
            return f"int: {x}"

        @foo.register
        def _(x: str, y: int):
            return f"str: {x}, int: {y}"

        @foo.register
        def _(x: str, y: float):
            return f"str: {x}, float: {y}"

        @foo.register
        def _(x: str, y: int, z: int):
            return f"str: {x}, int: {y}, int: {z}"

        @foo.register
        def _(x: int, y: float, z: int):
            return f"int: {x}, float: {y}, int: {z}"

        @foo.register
        def _(x: list, y: str = "default"):
            return f"int: {x}, str: {y}"

        @foo.register
        def _(x: list, y: list):
            return f"int: {x}, int: {y}"

        def test_case():
            foo()
            foo(10)
            foo("text", 10)
            foo("text", 10.5)
            foo("text", 10, 20)
            foo(10, 10.5, 20)
            foo("text", "text", "text")
            foo(x=10, y=20, z=30)
            foo(10, 20, 30)
            foo(x="text", y="text", z="text")
            foo("text", 10, 20, z=30)
            foo("text", 10, 20, z="30", a=40, b=50, c=60)
            foo([10])
            foo([10], "text")
            foo([10], y="custom")
            foo([10], [10])
            with self.assertRaises(MultiDispatchError):
                foo("text", ["list"])

        # Measure the execution time
        execution_time = timeit.timeit(test_case, number=100000)  # Run the test case 100000 times
        print(f"Execution time: {execution_time} seconds")


if __name__ == '__main__':
    unittest.main()

