import datetime
import operator
import unittest


class DatetimeTestCase(unittest.TestCase):

    def test_date_datetime(self):
        datetime_ = datetime.datetime.utcnow()
        date_ = datetime.date(2023, 2, 4)

        for op in ("ge", "gt", "le", "lt"):
            with self.subTest(op=op):
                self.assertRaises(TypeError,
                                  getattr(operator, op),
                                  date_,
                                  datetime_)
                self.assertRaises(TypeError,
                                  getattr(operator, op),
                                  datetime_,
                                  date_)


if __name__ == "__main__":
    unittest.main()
