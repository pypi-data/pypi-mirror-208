import unittest

from Factory import SerializerFactory
from for_tests import func, decorator, A, B, C
import unittest


class TestsForJson(unittest.TestCase):
    def setUp(self) -> None:
        self.serializer = SerializerFactory.serializer("json")

    def test_for_int(self):
        ser = self.serializer.dumps(27)
        des = self.serializer.loads(ser)

        self.assertEqual(des, 27)

    def test_for_float(self):
        ser = self.serializer.dumps(0.52)
        des = self.serializer.loads(ser)

        self.assertEqual(des, 0.52)

    def test_for_str(self):
        ser = self.serializer.dumps("test")
        des = self.serializer.loads(ser)

        self.assertEqual(des, "test")

    def test_for_bool(self):
        flag = True
        ser = self.serializer.dumps(flag)
        des = self.serializer.loads(ser)

        self.assertEqual(des, flag)

    def test_for_dict(self):
        test_dictionary = {"1": "apple", "2": "banana", "3": "orange"}
        ser = self.serializer.dumps(test_dictionary)
        des = self.serializer.loads(ser)

        self.assertEqual(des, test_dictionary)

    def test_for_list(self):
        test_list = ["Pasha", "Andrew", "Max", "Bob", "Alex"]
        ser = self.serializer.dumps(test_list)
        des = self.serializer.loads(ser)

        self.assertEqual(des, test_list)

    def test_for_set(self):
        test_set = {0.2, "bread", 5, "water", 5.7, 8}
        ser = self.serializer.dumps(test_set)
        des = self.serializer.loads(ser)

        self.assertEqual(des, test_set)

    def test_for_func(self):
        ser = self.serializer.dumps(func)
        des = self.serializer.loads(ser)

        self.assertEqual(des(25), func(25))

    def test_for_lambda_func(self):
        lambda_func = lambda x: x % 2 == 1
        ser = self.serializer.dumps(lambda_func)
        des = self.serializer.loads(ser)

        self.assertEqual(des(2), lambda_func(2))

    def test_for_decorator(self):
        dec = decorator(func)
        ser = self.serializer.dumps(decorator)
        des = self.serializer.loads(ser)
        func_des = des(func)

        self.assertEqual(func_des(4), dec(4))

    def test_for_class(self):
        test_class = C()
        ser = self.serializer.dumps(test_class)
        des = self.serializer.loads(ser)

        self.assertEqual(des.test1(), test_class.test1())

    def test_for_static_meth(self):
        static_meth = A()
        ser = self.serializer.dumps(static_meth)
        des = self.serializer.loads(ser)

        self.assertEqual(des.static_test1(), static_meth.static_test1())


class TestsForXML(unittest.TestCase):
    def setUp(self) -> None:
        self.serializer = SerializerFactory.serializer("xml")

    def test_for_int(self):
        ser = self.serializer.dumps(27)
        des = self.serializer.loads(ser)

        self.assertEqual(des, 27)

    def test_for_float(self):
        ser = self.serializer.dumps(0.52)
        des = self.serializer.loads(ser)

        self.assertEqual(des, 0.52)

    def test_for_str(self):
        string = "test"
        ser = self.serializer.dumps(string)
        des = self.serializer.loads(ser)

        self.assertEqual(des, string)

    def test_for_bool(self):
        flag = True
        ser = self.serializer.dumps(flag)
        des = self.serializer.loads(ser)

        self.assertEqual(des, flag)

    def test_for_dict(self):
        test_dictionary = {"1": "apple", "2": "banana", "3": "orange"}
        ser = self.serializer.dumps(test_dictionary)
        des = self.serializer.loads(ser)

        self.assertEqual(des, test_dictionary)

    def test_for_list(self):
        test_list = ["Pasha", "Andrew", "Max", "Bob", "Alex"]
        ser = self.serializer.dumps(test_list)
        des = self.serializer.loads(ser)

        self.assertEqual(des, test_list)

    def test_for_set(self):
        test_set = {0.2, "bread", 5, "water", 5.7, 8}
        ser = self.serializer.dumps(test_set)
        des = self.serializer.loads(ser)

        self.assertEqual(des, test_set)

    def test_for_func(self):
        ser = self.serializer.dumps(func)
        des = self.serializer.loads(ser)

        self.assertEqual(des(25), func(25))

    def test_for_lambda_func(self):
        lambda_func = lambda x: x % 2 == 1
        ser = self.serializer.dumps(lambda_func)
        des = self.serializer.loads(ser)

        self.assertEqual(des(2), lambda_func(2))

    def test_for_decorator(self):
        dec = decorator(func)
        ser = self.serializer.dumps(decorator)
        des = self.serializer.loads(ser)
        func_des = des(func)

        self.assertEqual(func_des(4), dec(4))

    def test_for_class(self):
        test_class = C()
        ser = self.serializer.dumps(test_class)
        des = self.serializer.loads(ser)

        self.assertEqual(des.test1(), test_class.test1())

    def test_for_static_meth(self):
        static_meth = A()
        ser = self.serializer.dumps(static_meth)
        des = self.serializer.loads(ser)

        self.assertEqual(des.static_test1(), static_meth.static_test1())

