import unittest
import os
import sys
import importlib

from .ser_deser_class import SerDeserClass

SerDeser = SerDeserClass()
SerDeserXML = SerDeserClass("xml")


def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

class MyClass:
    class_variable = "class_variable"

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def method(self, c):
        return self.a + self.b + c

    def method2(self, a: int, b: int, c: int):
        return self.a * a + self.b * b + c * c

    @staticmethod
    def static_method(d):
        return d

    @classmethod
    def class_method(cls, e):
        return cls.class_variable + e


class MySubclass(MyClass):
    def method(self, c):
        return 2 * self.a + 2 * self.b + c


class ClassSerDeser(unittest.TestCase):
    def test_class_serialization(self):
        my_class = MyClass(1, 2)
        deserialized = SerDeser.deserialize(SerDeser.serialize(my_class))
        deserialized_xml = SerDeserXML.deserialize(SerDeserXML.serialize(my_class))

        self.assertEqual(deserialized.a, 1)
        self.assertEqual(deserialized.b, 2)
        self.assertEqual(deserialized.method(3), my_class.method(3))

        self.assertEqual(deserialized_xml.a, 1)
        self.assertEqual(deserialized_xml.b, 2)
        self.assertEqual(deserialized_xml.method(3), my_class.method(3))

    def test_subclass_serialization(self):
        my_subclass = MySubclass(1, 2)

        deserialized = SerDeser.deserialize(SerDeser.serialize(my_subclass))
        deserialized_xml = SerDeserXML.deserialize(SerDeserXML.serialize(my_subclass))

        self.assertEqual(deserialized.a, 1)
        self.assertEqual(deserialized.b, 2)
        self.assertEqual(deserialized.method(4), my_subclass.method(4))
        self.assertEqual(deserialized.method2(2, 3, 4), my_subclass.method2(2, 3, 4))

        self.assertEqual(deserialized_xml.a, 1)
        self.assertEqual(deserialized_xml.b, 2)
        self.assertEqual(deserialized_xml.method(4), my_subclass.method(4))
        self.assertEqual(
            deserialized_xml.method2(2, 3, 4), my_subclass.method2(2, 3, 4)
        )

    def test_static_method_serialization(self):
        my_class = MyClass(1, 2)
        func = SerDeser.deserialize(SerDeser.serialize(my_class.static_method))
        self.assertEqual(func(5), MyClass.static_method(5))
        self.assertEqual(func(6), MyClass.static_method(6))
        self.assertEqual(func(7), MyClass.static_method(7))

        func = SerDeserXML.deserialize(SerDeserXML.serialize(my_class.static_method))
        self.assertEqual(func(5), MyClass.static_method(5))
        self.assertEqual(func(6), MyClass.static_method(6))
        self.assertEqual(func(7), MyClass.static_method(7))

    def test_class_method_serialization(self):
        my_class = MyClass(1, 2)
        func = SerDeser.deserialize(SerDeser.serialize(my_class.class_method))

        self.assertEqual(func("e"), MyClass.class_method("e"))
        self.assertEqual(func("fufufu"), MyClass.class_method("fufufu"))
        self.assertEqual(func("laba kal"), MyClass.class_method("laba kal"))

        func = SerDeserXML.deserialize(SerDeserXML.serialize(my_class.class_method))

        self.assertEqual(func("e"), MyClass.class_method("e"))
        self.assertEqual(func("fufufu"), MyClass.class_method("fufufu"))
        self.assertEqual(func("laba kal"), MyClass.class_method("laba kal"))

    def test_builtin_scope_serialization(self):
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize(len)), len)
        self.assertEqual(SerDeserXML.deserialize(SerDeserXML.serialize(len)), len)

    def test_nonlocal_scope_serialization(self):
        def outer_func():
            nonlocal_var = "nonlocal_var"

            def inner_func():
                self.assertEqual(
                    SerDeser.deserialize(SerDeser.serialize(nonlocal_var)), nonlocal_var
                )
                self.assertEqual(
                    SerDeserXML.deserialize(SerDeserXML.serialize(nonlocal_var)),
                    nonlocal_var,
                )

            inner_func()

        outer_func()

    def test_local_scope_serialization(self):
        def func():
            local_var = "local_var"
            self.assertEqual(
                SerDeser.deserialize(SerDeser.serialize(local_var)), local_var
            )
            self.assertEqual(
                SerDeserXML.deserialize(SerDeserXML.serialize(local_var)), local_var
            )

        func()


class BasicSerDeser(unittest.TestCase):
    def test_int(self):
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize(42)), 42)
        self.assertEqual(SerDeserXML.deserialize(SerDeserXML.serialize(42)), 42)

    def test_float(self):
        self.assertAlmostEqual(SerDeser.deserialize(SerDeser.serialize(3.14)), 3.14)
        self.assertAlmostEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize(3.14)), 3.14
        )

    def test_bool(self):
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize(True)), True)
        self.assertEqual(SerDeserXML.deserialize(SerDeserXML.serialize(True)), True)

    def test_str(self):
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize("hello")), "hello")
        self.assertEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize("hello")), "hello"
        )

    def test_none(self):
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize(None)), None)
        self.assertEqual(SerDeserXML.deserialize(SerDeserXML.serialize(None)), None)

    def test_tuple(self):
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize((1, 2, 3))), (1, 2, 3))
        self.assertEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize((1, 2, 3))), (1, 2, 3)
        )

    def test_list(self):
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize([1, 2, 3])), [1, 2, 3])
        self.assertEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize([1, 2, 3])), [1, 2, 3]
        )

    def test_set(self):
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize({1, 2, 3})), {1, 2, 3})
        self.assertEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize({1, 2, 3})), {1, 2, 3}
        )

    def test_dict(self):
        self.assertEqual(
            SerDeser.deserialize(SerDeser.serialize({"a": 1, "b": 2})), {"a": 1, "b": 2}
        )
        self.assertEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize({"a": 1, "b": 2})),
            {"a": 1, "b": 2},
        )

    def test_lambda(self):
        f = lambda x: x * 2
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize(f(3))), 6)
        self.assertEqual(SerDeserXML.deserialize(SerDeserXML.serialize(f(3))), 6)

    def test_closure(self):
        def outer():
            x = 10

            def inner():
                return x

            return inner

        inner_func = outer()
        self.assertEqual(SerDeser.deserialize(SerDeser.serialize(inner_func())), 10)
        self.assertEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize(inner_func())), 10
        )

    def test_recursion(self):        

        self.assertEqual(SerDeser.deserialize(SerDeser.serialize(factorial))(5), 120)
        self.assertEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize(factorial))(5), 120
        )

    def test_decorator(self):
        def my_decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs) * 2

            return wrapper

        @my_decorator
        def my_function(x):
            return x + 1

        self.assertEqual(SerDeser.deserialize(SerDeser.serialize(my_function))(3), 8)
        self.assertEqual(
            SerDeserXML.deserialize(SerDeserXML.serialize(my_function))(3), 8
        )


def do_test():
    unittest.main("serdeser_test")


if __name__ == "__main__":
    do_test()