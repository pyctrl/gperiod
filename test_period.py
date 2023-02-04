import copy
import datetime
import unittest

import period


FAKE_TS_01 = datetime.datetime(2019, 2, 1, 10, 0, 0)
FAKE_TS_02 = datetime.datetime(2019, 4, 14, 10, 0)
FAKE_TS_03 = datetime.datetime(2019, 5, 20, 10, 0)
FAKE_TS_04 = datetime.datetime(2019, 6, 25, 10, 0)
FAKE_TS_05 = datetime.datetime(2019, 7, 31, 10, 0)
FAKE_TS_06 = datetime.datetime(2019, 9, 5, 10, 0)
FAKE_TS_07 = datetime.datetime(2019, 10, 11, 10, 0)
FAKE_TS_08 = datetime.datetime(2019, 11, 16, 10, 0)
FAKE_TS_09 = datetime.datetime(2019, 12, 22, 10, 0)
FAKE_TS_10 = datetime.datetime(2020, 1, 27, 10, 0)
FAKE_TS_11 = datetime.datetime(2020, 3, 3, 10, 0)
FAKE_TS_12 = datetime.datetime(2020, 4, 8, 10, 0)
FAKE_TS_13 = datetime.datetime(2020, 5, 14, 10, 0)
FAKE_TS_14 = datetime.datetime(2020, 6, 19, 10, 0)
FAKE_TS_15 = datetime.datetime(2020, 7, 25, 10, 0)
FAKE_TS_16 = datetime.datetime(2020, 8, 30, 10, 0)
FAKE_TS_17 = datetime.datetime(2020, 10, 5, 10, 0)
FAKE_TS_18 = datetime.datetime(2020, 11, 10, 10, 0)
FAKE_TS_19 = datetime.datetime(2020, 12, 16, 10, 0)
FAKE_TS_20 = datetime.datetime(2021, 1, 21, 10, 0)
FAKE_TS_21 = datetime.datetime(2021, 2, 26, 10, 0)
FAKE_TS_22 = datetime.datetime(2021, 4, 3, 10, 0)
FAKE_TS_23 = datetime.datetime(2021, 5, 9, 10, 0)
FAKE_TS_24 = datetime.datetime(2021, 6, 14, 10, 0)
FAKE_TS_25 = datetime.datetime(2021, 7, 20, 10, 0)
FAKE_TS_26 = datetime.datetime(2021, 8, 25, 10, 0)
FAKE_TS_27 = datetime.datetime(2021, 9, 30, 10, 0)
FAKE_TS_28 = datetime.datetime(2021, 11, 5, 10, 0)
FAKE_TS_29 = datetime.datetime(2021, 12, 11, 10, 0)
FAKE_TS_30 = datetime.datetime(2022, 1, 16, 10, 0)


class TestCase(unittest.TestCase):

    def _assert_result_datetime(self, result, expected):
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], datetime.datetime)
        self.assertIsInstance(result[1], datetime.datetime)
        self.assertEqual(result, expected)

    def _assert_result_period(self, result, expected):
        self.assertIsInstance(result, period.Period)
        self.assertEqual(result, expected)


class PeriodBaseTestCase(TestCase):

    def test_init(self):
        result = period.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertIs(result.start, FAKE_TS_01)
        self.assertIs(result.end, FAKE_TS_02)
        self.assertIsInstance(result, period.Period)

    def test_modify(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)

        with self.subTest(attr=period._F_START):
            self.assertRaises(NotImplementedError,
                              setattr,
                              p,
                              period._F_START,
                              FAKE_TS_01)
        with self.subTest(attr=period._F_END):
            self.assertRaises(NotImplementedError,
                              setattr,
                              p,
                              period._F_END,
                              FAKE_TS_15)

    def test_delete(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)

        with self.subTest(attr=period._F_START):
            self.assertRaises(NotImplementedError,
                              delattr,
                              p,
                              period._F_START)
        with self.subTest(attr=period._F_END):
            self.assertRaises(NotImplementedError,
                              delattr,
                              p,
                              period._F_END)

    def test_hash(self):
        p1 = period.Period(FAKE_TS_05, FAKE_TS_10)
        p2 = period.Period(FAKE_TS_05, FAKE_TS_10)
        expected = hash((FAKE_TS_05, FAKE_TS_10))

        r1 = hash(p1)
        r2 = hash(p2)

        self.assertEqual(r1, r2)
        self.assertEqual(r1, expected)


class PeriodRepresentationTestCase(TestCase):

    def test_repr(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)
        expected = ("Period(datetime.datetime(2019, 7, 31, 10, 0),"
                    " datetime.datetime(2020, 1, 27, 10, 0))")

        result = repr(p)

        self.assertEqual(result, expected)

    def test_str(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)
        expected = p.to_isoformat()

        result = str(p)

        self.assertEqual(result, expected)

    def test_to_isoformat(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)
        expected = "2019-07-31T10:00:00/2020-01-27T10:00:00"

        result = p.to_isoformat()

        self.assertEqual(result, expected)

    def test_from_isoformat(self):
        s = "2019-07-31T10:00:00/2020-01-27T10:00:00"
        expected = period.Period(FAKE_TS_05, FAKE_TS_10)

        result = period.Period.from_isoformat(s)

        self.assertEqual(result, expected)

    def test_from_isoformat_failed(self):
        subtests = {
            "no_slash": "2019-07-31T10:00:002020-01-27T10:00:00",
            "many_slashes": "2019-07-3/1T10:00:00/2020-01-27T10:00:00",
        }

        for subtest, s in subtests.items():
            with self.subTest(subtest=subtest):
                self.assertRaises(ValueError, period.Period.from_isoformat, s)


class PeriodConvertTestCase(TestCase):

    def test_modcopy_copy(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)

        result = copy.copy(p)

        self.assertIsInstance(result, period.Period)
        self.assertIsNot(result, p)
        self.assertEqual(result, p)

    def test_copy(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)

        result = p.copy()

        self.assertIsInstance(result, period.Period)
        self.assertIsNot(result, p)
        self.assertEqual(result, p)

    def test_as_tuple(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)
        expected = (p.start, p.end)

        result = p.as_tuple()

        self._assert_result_datetime(result, expected)

    def test_as_dict(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)
        expected = dict(start=p.start, end=p.end)

        result = p.as_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)


class WithinTestCase(TestCase):

    def test_in(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_15)
        p_in = period.Period(FAKE_TS_08, FAKE_TS_12)
        p_left = period.Period(FAKE_TS_05, FAKE_TS_10)
        p_right = period.Period(FAKE_TS_10, FAKE_TS_15)
        p_same = period.Period(FAKE_TS_05, FAKE_TS_15)
        dt_in = FAKE_TS_10
        dt_left = FAKE_TS_05
        dt_right = FAKE_TS_15

        for item in (dt_in, dt_left, dt_right, p_in, p_left, p_right, p_same):
            with self.subTest(item=item):
                result = period.within(p, item)

                self.assertTrue(result)
                self.assertIsInstance(result, bool)

    def test_not_in(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_15)
        p_left = period.Period(FAKE_TS_01, FAKE_TS_02)
        p_touch_left = period.Period(FAKE_TS_01, FAKE_TS_05)
        p_cross_left = period.Period(FAKE_TS_02, FAKE_TS_10)
        p_right = period.Period(FAKE_TS_17, FAKE_TS_20)
        p_touch_right = period.Period(FAKE_TS_15, FAKE_TS_20)
        p_cross_right = period.Period(FAKE_TS_08, FAKE_TS_20)
        p_bigger = period.Period(FAKE_TS_01, FAKE_TS_25)
        dt_left = FAKE_TS_01
        dt_right = FAKE_TS_20

        for item in (dt_left, dt_right,
                     p_bigger,
                     p_left, p_touch_left, p_cross_left,
                     p_right, p_touch_right, p_cross_right):
            with self.subTest(item=item):
                result = period.within(p, item)

                self.assertFalse(result)
                self.assertIsInstance(result, bool)


class JoinTestCase(TestCase):

    def test_missing_args(self):
        p = period.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertRaises(TypeError, period.join)
        self.assertRaises(TypeError, period.join, flat=True)
        self.assertRaises(TypeError, period.join, p)
        self.assertRaises(TypeError, period.join, p, flat=True)

    def test_joined(self):
        p1 = period.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = period.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = period.Period(FAKE_TS_03, FAKE_TS_08)
        p4 = period.Period(FAKE_TS_08, FAKE_TS_10)
        expected = period.Period(FAKE_TS_01, FAKE_TS_10)

        result_p = period.join(p2, p4, p3, p1)
        result_dt = period.join(p2, p4, p3, p1, flat=True)

        self._assert_result_period(result_p, expected)
        self._assert_result_datetime(result_dt, expected.as_tuple())

    def test_not_joined(self):
        p1 = period.Period(FAKE_TS_01, FAKE_TS_02)
        p4 = period.Period(FAKE_TS_08, FAKE_TS_10)

        self.assertIsNone(period.join(p4, p1))
        self.assertIsNone(period.join(p4, p1, flat=True))


class UnionPeriodTestCase(TestCase):

    def test_missing_args(self):
        p = period.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertRaises(TypeError, period.union)
        self.assertRaises(TypeError, period.union, flat=True)
        self.assertRaises(TypeError, period.union, p)
        self.assertRaises(TypeError, period.union, p, flat=True)

    def test_empty(self):
        p1 = period.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = period.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = period.Period(FAKE_TS_03, FAKE_TS_04)
        p4 = period.Period(FAKE_TS_04, FAKE_TS_05)
        p5 = period.Period(FAKE_TS_05, FAKE_TS_06)
        subtests = {
            "ordered_2args_1": (p1, p3),
            "ordered_2args_2": (p2, p5),
            "ordered_Nargs_1": (p1, p3, p5),
            "reversed_2args_1": (p3, p1),
            "mixed": (p2, p1, p5),
            "duplicated": (p4, p1, p4, p4),
        }

        for subtest, periods in subtests.items():
            with self.subTest(subtest=subtest):
                self.assertIsNone(period.union(*periods))
                self.assertIsNone(period.union(*periods, flat=True))

    def test_succeeded(self):
        p1 = period.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = period.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = period.Period(FAKE_TS_03, FAKE_TS_08)
        # p4 = period.Period(FAKE_TS_08, FAKE_TS_10)
        subtests = {
            "ordered_joined_2args": (
                (p1, p2),
                period.Period(FAKE_TS_01, FAKE_TS_03)
            ),
            "ordered_joined_Nargs": (
                (p1, p2, p3),
                period.Period(FAKE_TS_01, FAKE_TS_08)
            ),
            "reversed_joined_2args": (
                (p2, p1),
                period.Period(FAKE_TS_01, FAKE_TS_03)
            ),
            "reversed_joined_Nargs": (
                (p3, p2, p1),
                period.Period(FAKE_TS_01, FAKE_TS_08)
            ),
        }

        for subtest, unit in subtests.items():
            periods, expected = unit
            with self.subTest(subtest=subtest):
                self._assert_result_period(period.union(*periods), expected)
                self._assert_result_datetime(period.union(*periods, flat=True),
                                             expected.as_tuple())


if __name__ == "__main__":
    unittest.main()
