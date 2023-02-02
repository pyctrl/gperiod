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


class PeriodTestCase(unittest.TestCase):

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


class PeriodConvertTestCase(unittest.TestCase):

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

        self.assertIsInstance(result, tuple)
        self.assertEqual(result, expected)

    def test_as_dict(self):
        p = period.Period(FAKE_TS_05, FAKE_TS_10)
        expected = dict(start=p.start, end=p.end)

        result = p.as_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)


class JoinResultPeriodTestCase(unittest.TestCase):

    def test_empty_args(self):
        self.assertRaises(TypeError, period.join)

    def test_single(self):
        p = period.Period(FAKE_TS_01, FAKE_TS_02)

        result = period.join(p)

        self.assertIsInstance(result, period.Period)
        self.assertEqual(result, p)
        self.assertIsNot(result, p)

    def test_multi(self):
        p1 = period.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = period.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = period.Period(FAKE_TS_03, FAKE_TS_08)
        expected = period.Period(FAKE_TS_01, FAKE_TS_08)

        result = period.join(p2, p3, p1)

        self.assertIsInstance(result, period.Period)
        self.assertEqual(result, expected)


class JoinResultDatetimeTestCase(unittest.TestCase):

    def test_empty_args(self):
        self.assertRaises(TypeError, period.join, return_datetime=True)

    def test_single(self):
        p = period.Period(FAKE_TS_01, FAKE_TS_02)

        result = period.join(p, flat=True)

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], datetime.datetime)
        self.assertIsInstance(result[1], datetime.datetime)
        self.assertEqual(result[0], FAKE_TS_01)
        self.assertEqual(result[1], FAKE_TS_02)

    def test_multi(self):
        p1 = period.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = period.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = period.Period(FAKE_TS_03, FAKE_TS_08)

        result = period.join(p2, p3, p1, flat=True)

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], datetime.datetime)
        self.assertIsInstance(result[1], datetime.datetime)
        self.assertEqual(result[0], FAKE_TS_01)
        self.assertEqual(result[1], FAKE_TS_08)
