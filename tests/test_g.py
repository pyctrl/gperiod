import copy
import datetime
import operator
import types
import unittest
from unittest import mock

from gperiod import f
from gperiod import g


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
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result, expected)

    def _assert_result_datetime_pair(self, result, expected):
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], datetime.datetime)
        self.assertIsInstance(result[1], datetime.datetime)
        self.assertEqual(result, expected)

    def _assert_result_period(self, result, expected):
        self.assertIsInstance(result, g.Period)
        self.assertEqual(result, expected)

    def _assert_generator(self, result, expected, item_validator):
        self.assertIsInstance(result, types.GeneratorType)
        result = list(result)
        self.assertEqual(len(result), len(expected))
        for r, e in zip(result, expected):
            item_validator(r, e)


class PeriodBaseTestCase(TestCase):

    def test_init(self):
        result = g.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertIs(result.start, FAKE_TS_01)
        self.assertIs(result.end, FAKE_TS_02)
        self.assertIsInstance(result, g.Period)

    def test_edge_start(self):
        delta = FAKE_TS_02 - FAKE_TS_01

        result = g.Period.from_start(FAKE_TS_01, delta)

        self.assertEqual(result.start, FAKE_TS_01)
        self.assertEqual(result.end, FAKE_TS_02)
        self.assertIsInstance(result, g.Period)

    def test_edge_end(self):
        delta = FAKE_TS_02 - FAKE_TS_01

        result = g.Period.from_end(FAKE_TS_02, delta)

        self.assertEqual(result.start, FAKE_TS_01)
        self.assertEqual(result.end, FAKE_TS_02)
        self.assertIsInstance(result, g.Period)

    def test_modify(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)

        with self.subTest(attr=g._F_START):
            self.assertRaises(NotImplementedError,
                              setattr,
                              p,
                              g._F_START,
                              FAKE_TS_01)
        with self.subTest(attr=g._F_END):
            self.assertRaises(NotImplementedError,
                              setattr,
                              p,
                              g._F_END,
                              FAKE_TS_15)

    def test_delete(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)

        with self.subTest(attr=g._F_START):
            self.assertRaises(NotImplementedError,
                              delattr,
                              p,
                              g._F_START)
        with self.subTest(attr=g._F_END):
            self.assertRaises(NotImplementedError,
                              delattr,
                              p,
                              g._F_END)

    def test_hash(self):
        p1 = g.Period(FAKE_TS_05, FAKE_TS_10)
        p2 = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = hash((FAKE_TS_05, FAKE_TS_10))

        r1 = hash(p1)
        r2 = hash(p2)

        self.assertEqual(r1, r2)
        self.assertEqual(r1, expected)

    def test_eq(self):
        sns = types.SimpleNamespace(start=FAKE_TS_05, end=FAKE_TS_10)
        p1 = g.Period(FAKE_TS_05, FAKE_TS_10)
        p2 = g.Period(FAKE_TS_05, FAKE_TS_10)
        p3 = g.Period(FAKE_TS_06, FAKE_TS_11)

        with self.subTest(subtest="equals"):
            self.assertTrue(p1 == p2)
            self.assertFalse(p1 != p2)
        with self.subTest(subtest="not_equals"):
            self.assertTrue(p1 != p3)
            self.assertFalse(p1 == p3)
        with self.subTest(subtest="sns"):
            self.assertFalse(sns == p1)
            self.assertTrue(sns != p1)
            self.assertFalse(sns == p3)
            self.assertTrue(sns != p3)
        with self.subTest(subtest="bad_type"):
            self.assertRaises(NotImplementedError, operator.eq, p1, p1.end)
            self.assertRaises(NotImplementedError, operator.eq, p1, 42)

    def test_in(self):
        p = g.Period(FAKE_TS_01, FAKE_TS_10)
        p_in = g.Period(FAKE_TS_04, FAKE_TS_06)
        dt = FAKE_TS_05
        subtests = {"datetime": dt, "period": p_in}

        for subtest, item in subtests.items():
            with self.subTest(subtest=subtest):
                self.assertIn(item, p)


class PeriodOperationsTestCase(TestCase):

    def test_add_delta(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        p = g.Period(dt1, dt2)
        delta = datetime.timedelta(days=2)
        expected = g.Period(dt1, dt3)

        with self.subTest(subtest="add"):
            self._assert_result_period(p + delta, expected)
        with self.subTest(subtest="radd"):
            self._assert_result_period(delta + p, expected)

    def test_add_period_success(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        p1 = g.Period(dt1, dt2)
        p2 = g.Period(dt2, dt3)
        expected = g.Period(dt1, dt3)

        with self.subTest(subtest="add"):
            self._assert_result_period(p1 + p2, expected)
        with self.subTest(subtest="radd"):
            self._assert_result_period(p2 + p1, expected)

    def test_add_period_failure(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        dt4 = datetime.datetime(2020, 1, 7, 10, 0, 0)
        p1 = g.Period(dt1, dt2)
        p2 = g.Period(dt3, dt4)

        with self.subTest(subtest="add"):
            self.assertIsNone(p1 + p2)
        with self.subTest(subtest="radd"):
            self.assertIsNone(p2 + p1)

    def test_and_period_success(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        dt4 = datetime.datetime(2020, 1, 7, 10, 0, 0)
        p1 = g.Period(dt1, dt3)
        p2 = g.Period(dt2, dt4)
        expected = g.Period(dt2, dt3)

        with self.subTest(subtest="and"):
            self._assert_result_period(p1 & p2, expected)
        with self.subTest(subtest="rand"):
            self._assert_result_period(p2 & p1, expected)

    def test_and_period_failure(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        dt4 = datetime.datetime(2020, 1, 7, 10, 0, 0)
        p1 = g.Period(dt1, dt2)
        p2 = g.Period(dt3, dt4)

        with self.subTest(subtest="and"):
            self.assertIsNone(p1 & p2)
        with self.subTest(subtest="rand"):
            self.assertIsNone(p2 & p1)

    def test_or_period_success(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        dt4 = datetime.datetime(2020, 1, 7, 10, 0, 0)
        p1 = g.Period(dt1, dt3)
        p2 = g.Period(dt2, dt4)
        expected = g.Period(dt1, dt4)

        with self.subTest(subtest="or"):
            self._assert_result_period(p1 | p2, expected)
        with self.subTest(subtest="ror"):
            self._assert_result_period(p2 | p1, expected)

    def test_or_period_failure(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        dt4 = datetime.datetime(2020, 1, 7, 10, 0, 0)
        p1 = g.Period(dt1, dt2)
        p2 = g.Period(dt3, dt4)

        with self.subTest(subtest="or"):
            self.assertIsNone(p1 | p2)
        with self.subTest(subtest="ror"):
            self.assertIsNone(p2 | p1)

    def test_lshift(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        dt4 = datetime.datetime(2020, 1, 7, 10, 0, 0)
        p = g.Period(dt2, dt4)
        delta = datetime.timedelta(days=2)
        expected = g.Period(dt1, dt3)

        self._assert_result_period(p << delta, expected)

    def test_rshift(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        dt3 = datetime.datetime(2020, 1, 5, 10, 0, 0)
        dt4 = datetime.datetime(2020, 1, 7, 10, 0, 0)
        p = g.Period(dt1, dt3)
        delta = datetime.timedelta(days=2)
        expected = g.Period(dt2, dt4)

        self._assert_result_period(p >> delta, expected)

    def test_shift_invalid(self):
        dt1 = datetime.datetime(2020, 1, 1, 10, 0, 0)
        dt2 = datetime.datetime(2020, 1, 3, 10, 0, 0)
        p = g.Period(dt1, dt2)

        with self.subTest(subtest="lshift"):
            self.assertRaises(NotImplementedError, operator.lshift, p, 42)
        with self.subTest(subtest="rshift"):
            self.assertRaises(NotImplementedError, operator.rshift, p, 42)


class PeriodRepresentationTestCase(TestCase):

    def test_repr(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = ("Period(datetime.datetime(2019, 7, 31, 10, 0),"
                    " datetime.datetime(2020, 1, 27, 10, 0))")

        result = repr(p)

        self.assertEqual(result, expected)

    def test_str(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = p.isoformat()

        result = str(p)

        self.assertEqual(result, expected)

    def test_to_isoformat(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = "2019-07-31T10:00:00/2020-01-27T10:00:00"

        result = p.isoformat()

        self.assertEqual(result, expected)

    def test_from_isoformat(self):
        s = "2019-07-31T10:00:00/2020-01-27T10:00:00"
        expected = g.Period(FAKE_TS_05, FAKE_TS_10)

        result = g.Period.fromisoformat(s)

        self.assertEqual(result, expected)

    def test_from_isoformat_failed(self):
        subtests = {
            "no_slash": "2019-07-31T10:00:002020-01-27T10:00:00",
            "many_slashes": "2019-07-3/1T10:00:00/2020-01-27T10:00:00",
        }

        for subtest, s in subtests.items():
            with self.subTest(subtest=subtest):
                self.assertRaises(ValueError, g.Period.fromisoformat, s)

    def test_strptime_simple(self):
        s = "2019-07-31T10:00:00/2020-01-27T10:00:00"
        expected = g.Period(FAKE_TS_05, FAKE_TS_10)

        result = g.Period.strptime(s, "%Y-%m-%dT%H:%M:%S")

        self.assertEqual(result, expected)

    def test_strptime_hard(self):
        s = "2019-07-31//10:00:00//2020-01-27//10:00:00"
        expected = g.Period(FAKE_TS_05, FAKE_TS_10)

        result = g.Period.strptime(s, "%Y-%m-%d//%H:%M:%S", sep="//")

        self.assertEqual(result, expected)

    def test_strptime_failed(self):
        subtests = {
            "no_slash": "2019-07-31T10:00:002020-01-27T10:00:00",
            "many_slashes": "2019-07-3/1T10:00:00/2020-01-27T10:00:00",
        }

        for subtest, s in subtests.items():
            with self.subTest(subtest=subtest):
                self.assertRaises(ValueError,
                                  g.Period.strptime,
                                  s,
                                  "%Y-%m-%d/%H:%M:%S")

    def test_strftime_simple(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = "2019-07-31T10:00:00/2020-01-27T10:00:00"

        result = p.strftime("%Y-%m-%dT%H:%M:%S")

        self.assertEqual(result, expected)

    def test_strftime_hard(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = "2019-07-31//10:00:00//2020-01-27//10:00:00"

        result = p.strftime("%Y-%m-%d//%H:%M:%S", sep="//")

        self.assertEqual(result, expected)


class PeriodConvertTestCase(TestCase):

    def test_modcopy_copy(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)

        result = copy.copy(p)

        self.assertIsInstance(result, g.Period)
        self.assertIsNot(result, p)
        self.assertEqual(result, p)

    def test_copy(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)

        result = p.copy()

        self.assertIsInstance(result, g.Period)
        self.assertIsNot(result, p)
        self.assertEqual(result, p)

    def test_as_tuple(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = (p.start, p.end)

        result = p.as_tuple()

        self._assert_result_datetime_pair(result, expected)

    def test_as_kwargs(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = dict(start=p.start, end=p.end)

        result = p.as_kwargs()

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)

    def test_as_dict(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)
        expected = dict(start=p.start, end=p.end, duration=p.duration)

        result = p.as_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)

    def test_replace_empty(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)

        result = p.replace()

        self.assertIsInstance(result, g.Period)
        self.assertIsNot(result, p)
        self.assertEqual(result, p)

    def test_replace_partial(self):
        expected = g.Period(FAKE_TS_01, FAKE_TS_10)

        p = g.Period(FAKE_TS_05, FAKE_TS_10)

        result = p.replace(FAKE_TS_01)

        self.assertIsInstance(result, g.Period)
        self.assertIsNot(result, p)
        self.assertNotEqual(result, p)
        self.assertEqual(result, expected)

    def test_replace_full(self):
        expected = g.Period(FAKE_TS_01, FAKE_TS_06)

        p = g.Period(FAKE_TS_05, FAKE_TS_10)

        result = p.replace(FAKE_TS_01, end=FAKE_TS_06)

        self.assertIsInstance(result, g.Period)
        self.assertIsNot(result, p)
        self.assertNotEqual(result, p)
        self.assertEqual(result, expected)

    def test_replace_over(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_10)

        self.assertRaises(TypeError, p.replace,
                          start=FAKE_TS_01, something=FAKE_TS_06)
        self.assertRaises(TypeError, p.replace,
                          FAKE_TS_01, FAKE_TS_06, FAKE_TS_02, FAKE_TS_02)


class XscendYTestCase(TestCase):

    def test_asc_start(self):
        p1 = g.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = g.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = g.Period(FAKE_TS_03, FAKE_TS_08)
        p4 = g.Period(FAKE_TS_08, FAKE_TS_10)
        expected = [p1, p2, p3, p4]

        with self.subTest(subtest="forward"):
            result = g.ascend_start(p2, p3, p1, p4)
            self.assertEqual(result, expected)
        with self.subTest(subtest="forward_2"):
            result = g.ascend_start(p3, p1, p4, p2, reverse=False)
            self.assertEqual(result, expected)
        with self.subTest(subtest="backward"):
            result = g.ascend_start(p1, p4, p3, p2, reverse=True)
            self.assertEqual(result, expected[::-1])

    def test_desc_end(self):
        p1 = g.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = g.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = g.Period(FAKE_TS_03, FAKE_TS_08)
        p4 = g.Period(FAKE_TS_08, FAKE_TS_10)
        expected = [p4, p3, p2, p1]

        with self.subTest(subtest="forward"):
            result = f.descend_end(p4, p1, p2, p3)
            self.assertEqual(result, expected)
        with self.subTest(subtest="forward_2"):
            result = f.descend_end(p1, p2, p3, p4, reverse=False)
            self.assertEqual(result, expected)
        with self.subTest(subtest="backward"):
            result = f.descend_end(p3, p2, p1, p4, reverse=True)
            self.assertEqual(result, expected[::-1])


class ValidateEdgesTestCase(TestCase):

    def test_bad_type(self):
        with self.subTest(subtest="start"):
            self.assertRaises(TypeError, g.validate_edges, 42, FAKE_TS_10)
            self.assertRaises(TypeError, g.validate_edges,
                              start=42, end=FAKE_TS_10)
        with self.subTest(subtest="end"):
            self.assertRaises(TypeError, g.validate_edges, FAKE_TS_10, 42)
            self.assertRaises(TypeError, g.validate_edges,
                              start=FAKE_TS_10, end=42)

    def test_naive_aware(self):
        aware = datetime.datetime.fromisoformat("2000-02-26T10:21:12+03:00")
        naive = FAKE_TS_01

        self.assertRaises(ValueError, g.validate_edges,
                          aware, naive)
        self.assertRaises(ValueError, g.validate_edges,
                          naive, aware)

    def test_bad_direction(self):
        self.assertRaises(ValueError, g.validate_edges,
                          FAKE_TS_10, FAKE_TS_02)

    def test_bad_duration(self):
        self.assertRaises(ValueError, g.validate_edges,
                          FAKE_TS_10, FAKE_TS_10)

    def test_ok(self):
        g.validate_edges(FAKE_TS_05, FAKE_TS_10)


class ValidatePeriodTestCase(TestCase):

    @mock.patch("gperiod.g.validate_edges", __name__="validate_edges")
    def test_validate(self, mock_flat):
        g.Period(FAKE_TS_05, FAKE_TS_15)

        # g.validate_period(p)

        mock_flat.assert_called_once_with(FAKE_TS_05, FAKE_TS_15)


class WithinTestCase(TestCase):

    def test_in(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_15)
        p_in = g.Period(FAKE_TS_08, FAKE_TS_12)
        p_left = g.Period(FAKE_TS_05, FAKE_TS_10)
        p_right = g.Period(FAKE_TS_10, FAKE_TS_15)
        p_same = g.Period(FAKE_TS_05, FAKE_TS_15)
        dt_in = FAKE_TS_10
        dt_left = FAKE_TS_05
        dt_right = FAKE_TS_15

        for item in (dt_in, dt_left, dt_right, p_in, p_left, p_right, p_same):
            with self.subTest(item=item):
                result = g.contains(p, item)

                self.assertTrue(result)
                self.assertIsInstance(result, bool)

    def test_not_in(self):
        p = g.Period(FAKE_TS_05, FAKE_TS_15)
        p_left = g.Period(FAKE_TS_01, FAKE_TS_02)
        p_touch_left = g.Period(FAKE_TS_01, FAKE_TS_05)
        p_cross_left = g.Period(FAKE_TS_02, FAKE_TS_10)
        p_right = g.Period(FAKE_TS_17, FAKE_TS_20)
        p_touch_right = g.Period(FAKE_TS_15, FAKE_TS_20)
        p_cross_right = g.Period(FAKE_TS_08, FAKE_TS_20)
        p_bigger = g.Period(FAKE_TS_01, FAKE_TS_25)
        dt_left = FAKE_TS_01
        dt_right = FAKE_TS_20

        for item in (dt_left, dt_right,
                     p_bigger,
                     p_left, p_touch_left, p_cross_left,
                     p_right, p_touch_right, p_cross_right):
            with self.subTest(item=item):
                result = g.contains(p, item)

                self.assertFalse(result)
                self.assertIsInstance(result, bool)


class JoinTestCase(TestCase):

    def test_missing_args(self):
        p = g.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertRaises(TypeError, g.join)
        self.assertRaises(TypeError, g.join, factory=g.Tuple)
        self.assertRaises(TypeError, g.join, p)
        self.assertRaises(TypeError, g.join, p, factory=g.Tuple)

    def test_joined(self):
        p1 = g.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = g.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = g.Period(FAKE_TS_03, FAKE_TS_08)
        p4 = g.Period(FAKE_TS_08, FAKE_TS_10)
        expected = g.Period(FAKE_TS_01, FAKE_TS_10)

        result_p = g.join(p2, p4, p3, p1)
        result_dt = g.join(p2, p4, p3, p1, factory=g.Tuple)

        self._assert_result_period(result_p, expected)
        self._assert_result_datetime_pair(result_dt, expected.as_tuple())

    def test_not_joined(self):
        p1 = g.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = g.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = g.Period(FAKE_TS_03, FAKE_TS_04)
        p4 = g.Period(FAKE_TS_04, FAKE_TS_05)
        p5 = g.Period(FAKE_TS_05, FAKE_TS_06)
        subtests = {
            "ordered_2args_1": (p1, p3),
            "ordered_2args_2": (p2, p5),
            "ordered_Nargs_1": (p1, p3, p5),
            "reversed_2args_1": (p3, p1),
            "reversed_Nargs_1": (p5, p3, p1),
            "mixed": (p2, p1, p5),
            "duplicated": (p4, p1, p4, p4),
        }

        for subtest, periods in subtests.items():
            with self.subTest(subtest=subtest):
                self.assertIsNone(g.join(*periods))
                self.assertIsNone(g.join(*periods, factory=g.Tuple))


class UnionTestCase(TestCase):

    def test_missing_args(self):
        p = g.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertRaises(TypeError, g.union)
        self.assertRaises(TypeError, g.union, factory=g.Tuple)
        self.assertRaises(TypeError, g.union, p)
        self.assertRaises(TypeError, g.union, p, factory=g.Tuple)

    def test_empty(self):
        p1 = g.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = g.Period(FAKE_TS_02, FAKE_TS_03)
        p3 = g.Period(FAKE_TS_03, FAKE_TS_04)
        p4 = g.Period(FAKE_TS_04, FAKE_TS_05)
        p5 = g.Period(FAKE_TS_05, FAKE_TS_06)
        subtests = {
            "ordered_2args_1": (p1, p3),
            "ordered_2args_2": (p2, p5),
            "ordered_Nargs_1": (p1, p3, p5),
            "reversed_2args_1": (p3, p1),
            "reversed_Nargs_1": (p5, p3, p1),
            "mixed": (p2, p1, p5),
            "duplicated": (p4, p1, p4, p4),
        }

        for subtest, periods in subtests.items():
            with self.subTest(subtest=subtest):
                self.assertIsNone(g.union(*periods))
                self.assertIsNone(g.union(*periods, factory=g.Tuple))

    def test_succeeded(self):
        p1a = g.Period(FAKE_TS_01, FAKE_TS_03)
        p1b = g.Period(FAKE_TS_02, FAKE_TS_05)
        p2 = g.Period(FAKE_TS_03, FAKE_TS_04)
        p3 = g.Period(FAKE_TS_04, FAKE_TS_08)
        subtests = {
            "ordered_joined_2args_1": (
                (p1a, p2),
                g.Period(FAKE_TS_01, FAKE_TS_04),
            ),
            "ordered_joined_2args_2": (
                (p1a, p1b),
                g.Period(FAKE_TS_01, FAKE_TS_05),
            ),
            "ordered_joined_Nargs": (
                (p1a, p2, p3),
                g.Period(FAKE_TS_01, FAKE_TS_08),
            ),
            "reversed_joined_2args": (
                (p2, p1a),
                g.Period(FAKE_TS_01, FAKE_TS_04),
            ),
            "reversed_joined_Nargs": (
                (p3, p2, p1a),
                g.Period(FAKE_TS_01, FAKE_TS_08),
            ),
        }

        for subtest, unit in subtests.items():
            periods, expected = unit
            with self.subTest(subtest=subtest):
                self._assert_result_period(g.union(*periods), expected)
                self._assert_result_datetime_pair(
                    g.union(*periods, factory=g.Tuple),
                    expected.as_tuple(),
                )


class IntersectionTestCase(TestCase):

    def test_missing_args(self):
        p = g.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertRaises(TypeError, g.intersection)
        self.assertRaises(TypeError, g.intersection, factory=g.Tuple)
        self.assertRaises(TypeError, g.intersection, p)
        self.assertRaises(TypeError, g.intersection, p, factory=g.Tuple)

    def test_empty(self):
        p1 = g.Period(FAKE_TS_01, FAKE_TS_08)
        p2 = g.Period(FAKE_TS_04, FAKE_TS_12)
        p3 = g.Period(FAKE_TS_08, FAKE_TS_16)
        p4 = g.Period(FAKE_TS_12, FAKE_TS_20)
        p5 = g.Period(FAKE_TS_16, FAKE_TS_24)
        subtests = {
            "ordered_2args_1": (p1, p3),
            "ordered_2args_2": (p2, p5),
            "ordered_Nargs_1": (p1, p3, p5),
            "reversed_2args_1": (p3, p1),
            "reversed_Nargs_1": (p5, p3, p1),
            "mixed": (p3, p1, p5),
            "duplicated": (p4, p1, p4, p4),
        }

        for subtest, periods in subtests.items():
            with self.subTest(subtest=subtest):
                self.assertIsNone(g.intersection(*periods))
                self.assertIsNone(g.intersection(*periods, factory=g.Tuple))

    def test_succeeded(self):
        p1 = g.Period(FAKE_TS_01, FAKE_TS_08)
        p2 = g.Period(FAKE_TS_04, FAKE_TS_12)
        p3 = g.Period(FAKE_TS_06, FAKE_TS_16)
        subtests = {
            "ordered_joined_2args_1": (
                (p1, p2),
                g.Period(FAKE_TS_04, FAKE_TS_08),
            ),
            "ordered_joined_Nargs": (
                (p1, p2, p3),
                g.Period(FAKE_TS_06, FAKE_TS_08),
            ),
            "reversed_joined_2args": (
                (p2, p1),
                g.Period(FAKE_TS_04, FAKE_TS_08),
            ),
            "reversed_joined_Nargs": (
                (p3, p2, p1),
                g.Period(FAKE_TS_06, FAKE_TS_08),
            ),
        }

        for subtest, unit in subtests.items():
            periods, expected = unit
            with self.subTest(subtest=subtest):
                self._assert_result_period(
                    g.intersection(*periods),
                    expected,
                )
                self._assert_result_datetime_pair(
                    g.intersection(*periods, factory=g.Tuple),
                    expected.as_tuple(),
                )


class ToTimestampsTestCase(TestCase):

    def test_empty(self):
        self._assert_generator(
                    f.to_timestamps(),
                    [],
                    self._assert_result_datetime)

    def test_single(self):
        p = g.Period(FAKE_TS_01, FAKE_TS_02)

        self._assert_generator(
                    f.to_timestamps(p),
                    [FAKE_TS_01, FAKE_TS_02],
                    self._assert_result_datetime)

    def test_multi(self):
        p1 = g.Period(FAKE_TS_01, FAKE_TS_02)
        p2 = g.Period(FAKE_TS_03, FAKE_TS_04)
        p3 = g.Period(FAKE_TS_04, FAKE_TS_05)
        p4 = g.Period(FAKE_TS_04, FAKE_TS_05)

        self._assert_generator(
                    f.to_timestamps(p1, p2, p3, p4),
                    [FAKE_TS_01, FAKE_TS_02, FAKE_TS_03, FAKE_TS_04,
                     FAKE_TS_04, FAKE_TS_05, FAKE_TS_04, FAKE_TS_05],
                    self._assert_result_datetime)


class DifferenceTestCase(TestCase):

    def test_missing_args(self):
        p = g.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertRaises(TypeError, g.difference)
        self.assertRaises(TypeError, g.difference, factory=g.Tuple)
        self.assertRaises(TypeError, g.difference, p)
        self.assertRaises(TypeError, g.difference, p, factory=g.Tuple)

    def test_no_dif(self):
        p = g.Period(FAKE_TS_08, FAKE_TS_16)
        expected = []
        subtests = {
            "same_2args": (g.Period(FAKE_TS_08, FAKE_TS_16),),
            "bigger_left_2args": (g.Period(FAKE_TS_04, FAKE_TS_16),),
            "bigger_right_2args": (g.Period(FAKE_TS_08, FAKE_TS_20),),
            "bigger_both_2args": (g.Period(FAKE_TS_04, FAKE_TS_20),),
            # "out_left_Nargs": (FAKE_TS_01, FAKE_TS_02, FAKE_TS_02),
            # "border_left_Nargs": (FAKE_TS_01, FAKE_TS_01, FAKE_TS_08),
            # "border_right_Nargs": (FAKE_TS_16, FAKE_TS_16, FAKE_TS_20),
            # "out_right_Nargs": (FAKE_TS_18, FAKE_TS_18, FAKE_TS_20),
        }

        for subtest, periods in subtests.items():
            with self.subTest(subtest=subtest):
                self._assert_generator(
                    g.difference(p, *periods),
                    expected,
                    self._assert_result_period,
                )
                self._assert_generator(
                    g.difference(p, *periods, factory=g.Tuple),
                    expected,
                    self._assert_result_datetime_pair,
                )

    def test_dif_1(self):
        p = g.Period(FAKE_TS_08, FAKE_TS_16)
        subtests = {
            "left_2args": (
                (g.Period(FAKE_TS_01, FAKE_TS_06),),
                [g.Period(FAKE_TS_08, FAKE_TS_16)],
            ),
            "left_border_2args": (
                (g.Period(FAKE_TS_01, FAKE_TS_08),),
                [g.Period(FAKE_TS_08, FAKE_TS_16)],
            ),
            "right_border_2args": (
                (g.Period(FAKE_TS_16, FAKE_TS_20),),
                [g.Period(FAKE_TS_08, FAKE_TS_16)],
            ),
            "right_2args": (
                (g.Period(FAKE_TS_20, FAKE_TS_25),),
                [g.Period(FAKE_TS_08, FAKE_TS_16)],
            ),
            "left_invade_2args": (
                (g.Period(FAKE_TS_01, FAKE_TS_12),),
                [g.Period(FAKE_TS_12, FAKE_TS_16)],
            ),
            "right_invade_2args": (
                (g.Period(FAKE_TS_12, FAKE_TS_20),),
                [g.Period(FAKE_TS_08, FAKE_TS_12)],
            ),
            "invade_2args": (
                (g.Period(FAKE_TS_10, FAKE_TS_12),),
                [g.Period(FAKE_TS_08, FAKE_TS_10),
                 g.Period(FAKE_TS_12, FAKE_TS_16)],
            ),
        }

        for subtest, unit in subtests.items():
            periods, expected = unit
            with self.subTest(subtest=subtest):
                self._assert_generator(
                    g.difference(p, *periods),
                    expected,
                    self._assert_result_period,
                )
                self._assert_generator(
                    g.difference(p, *periods, factory=g.Tuple),
                    [exp.as_tuple() for exp in expected],
                    self._assert_result_datetime_pair,
                )

    def test_dif_multi(self):
        p = g.Period(FAKE_TS_08, FAKE_TS_24)
        subtests = {
            "left_Nnargs": (
                (g.Period(FAKE_TS_01, FAKE_TS_06),
                 g.Period(FAKE_TS_03, FAKE_TS_07)),
                [g.Period(FAKE_TS_08, FAKE_TS_24)],
            ),

            # "left_border_2args": (
            #     (g.Period(FAKE_TS_01, FAKE_TS_08),),
            #     [g.Period(FAKE_TS_08, FAKE_TS_16)],
            # ),
            # "right_border_2args": (
            #     (g.Period(FAKE_TS_16, FAKE_TS_20),),
            #     [g.Period(FAKE_TS_08, FAKE_TS_16)],
            # ),
            # "right_2args": (
            #     (g.Period(FAKE_TS_20, FAKE_TS_25),),
            #     [g.Period(FAKE_TS_08, FAKE_TS_16)],
            # ),
            # "left_invade_2args": (
            #     (g.Period(FAKE_TS_01, FAKE_TS_12),),
            #     [g.Period(FAKE_TS_12, FAKE_TS_16)],
            # ),
            # "right_invade_2args": (
            #     (g.Period(FAKE_TS_12, FAKE_TS_20),),
            #     [g.Period(FAKE_TS_08, FAKE_TS_12)],
            # ),
            "invade_Nargs": (
                (g.Period(FAKE_TS_04, FAKE_TS_06),
                 g.Period(FAKE_TS_09, FAKE_TS_11),
                 g.Period(FAKE_TS_10, FAKE_TS_13),
                 g.Period(FAKE_TS_15, FAKE_TS_18),
                 g.Period(FAKE_TS_17, FAKE_TS_19),
                 ),
                [g.Period(FAKE_TS_08, FAKE_TS_09),
                 g.Period(FAKE_TS_13, FAKE_TS_15),
                 g.Period(FAKE_TS_19, FAKE_TS_24),
                 ],
            ),
        }

        for subtest, unit in subtests.items():
            periods, expected = unit
            with self.subTest(subtest=subtest):
                self._assert_generator(
                    g.difference(p, *periods),
                    expected,
                    self._assert_result_period,
                )
                self._assert_generator(
                    g.difference(p, *periods, factory=g.Tuple),
                    [exp.as_tuple() for exp in expected],
                    self._assert_result_datetime_pair,
                )


if __name__ == "__main__":
    unittest.main()
