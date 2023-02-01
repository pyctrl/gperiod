import datetime
import unittest

import period


FAKE_TS_01 = datetime.datetime(2019, 2, 1, 10, 0, 0)
FAKE_TS_02 = datetime.datetime(2019, 4, 14, 10, 0)


class PeriodTestCase(unittest.TestCase):

    def test_init(self):
        result = period.Period(FAKE_TS_01, FAKE_TS_02)

        self.assertIs(result.start, FAKE_TS_01)
        self.assertIs(result.end, FAKE_TS_02)
        self.assertIsInstance(result, period.Period)
