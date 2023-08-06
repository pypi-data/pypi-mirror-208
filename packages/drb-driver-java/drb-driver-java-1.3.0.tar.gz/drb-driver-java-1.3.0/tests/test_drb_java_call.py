import os


_CLASSPATH_ADDON = os.getenv('CLASSPATH_ADDON')
_HERE = os.path.dirname(__file__)
_HERE = os.pathsep.join([os.path.join(_HERE, "..")])

_PATH_TEST = os.pathsep.join([os.path.join(_HERE, "tests/files/*")])
if _CLASSPATH_ADDON is None:
    os.environ['CLASSPATH_ADDON'] = _PATH_TEST
else:
    os.environ['CLASSPATH_ADDON'] = _PATH_TEST + ":" + _CLASSPATH_ADDON
import time   # noqa: E402
import unittest   # noqa: E402
from pathlib import Path   # noqa: E402
# Set it before import JavaCall to indicate that classpath must be adapted
# for test
from drb.drivers.java.drb_driver_java_call import JavaCall   # noqa: E402


class TestDrbJavaCall(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    def test_Value_native_type(self):
        print('\n\n')

        DrbByte = JavaCall.get_auto_class("fr.gael.drb.value.Byte")
        test = DrbByte(0x41)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 65)

        DrbShort = JavaCall.get_auto_class("fr.gael.drb.value.Short")
        test = DrbShort(241)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 241)

        DrbInt = JavaCall.get_auto_class("fr.gael.drb.value.Int")
        test = DrbInt(1664)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 1664)

        DrbLong = JavaCall.get_auto_class("fr.gael.drb.value.Long")
        test = DrbLong(99999)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 99999)

        DrbFloat = JavaCall.get_auto_class("fr.gael.drb.value.Float")
        test = DrbFloat(3.1)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertAlmostEqual(test_value, 3.1, delta=0.1)

        DrbDouble = JavaCall.get_auto_class("fr.gael.drb.value.Double")
        test = DrbDouble(3.14e+10)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 3.14e+10)

        DrbString = JavaCall.get_auto_class("fr.gael.drb.value.String")
        test = DrbString("test")
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, "test")

        second_1970 = time.time()
        second_1970 -= time.timezone
        DrbDateTime = JavaCall.get_auto_class("fr.gael.drb.value.DateTime")
        test = DrbDateTime()
        test_value = JavaCall.cast_value_to_native_type(test)
        print(test_value)

        DrbNum = JavaCall.get_auto_class("fr.gael.drb.value.Int")
        test = DrbNum(999)
        test_value = JavaCall.cast_value_to_native_type(test, 9)
        self.assertEqual(test_value, 999)

        DrbBynaryInt = JavaCall.\
            get_auto_class("fr.gael.drb.value.BinaryInteger")
        # Paillette is born
        test = DrbBynaryInt(1596)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 1596)

        UnsignedByte = JavaCall.\
            get_auto_class("fr.gael.drb.value.UnsignedByte")
        test = UnsignedByte(33)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 0x21)

        UnsignedShort = JavaCall.\
            get_auto_class("fr.gael.drb.value.UnsignedShort")
        test = UnsignedShort(2036)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 2036)

        UnsignedInt = JavaCall.get_auto_class("fr.gael.drb.value.UnsignedInt")
        test = UnsignedInt(1240)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 1240)

        UnsignedLong = JavaCall.\
            get_auto_class("fr.gael.drb.value.UnsignedLong")
        test = UnsignedLong(789000)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 789000)

        Duration = JavaCall.get_auto_class("fr.gael.drb.value.Duration")
        test = Duration(0, 3600)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 3600)

        DayTimeDuration = JavaCall.\
            get_auto_class("fr.gael.drb.value.DayTimeDuration")
        test = DayTimeDuration('P2D')
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 3600*24*2)

        YearMonthDuration = JavaCall.\
            get_auto_class("fr.gael.drb.value.YearMonthDuration")
        test = YearMonthDuration(2)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 2)

        DrbBynaryInt = JavaCall.get_auto_class("fr.gael.drb.value.Int")
        # Mathias M is born
        test = DrbBynaryInt(1970)
        # fake type => string
        test_value = JavaCall.cast_value_to_native_type(test, 32)
        self.assertEqual(test_value, "1970")

        DrbDecimal = JavaCall.get_auto_class("fr.gael.drb.value.Decimal")
        test = DrbDecimal(0.10)
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 0.10)

        DrbInteger = JavaCall.get_auto_class("fr.gael.drb.value.Integer")
        test = DrbInteger('1234567891234567891234546789123456789')
        # In Python not Biginteger int is OK to have big value...
        test_value = JavaCall.cast_value_to_native_type(test)
        self.assertEqual(test_value, 1234567891234567891234546789123456789)

    def test_Value_array(self):
        DrbIntArray = JavaCall.get_auto_class("fr.gael.drb.value.IntArray")
        test_array = DrbIntArray(5)

        for index in range(5):
            test_array.assign(index, index*3)

        test_value = JavaCall.cast_value_to_native_type(test_array)

        self.assertEqual(len(test_value), 5)
        index = 0
        for value in test_value:
            self.assertEqual(JavaCall.cast_value_to_native_type(value),
                             index*3)
            index = index + 1
