# import typing
import unittest
import logging

from tkmilan.validation import StaticList, StaticMap, StaticMapLabels, StaticMapValues
from tkmilan.validation import LimitBounded, LimitUnbounded
from tkmilan import fn

logger = logging.getLogger(__name__)


class Test_StaticList(unittest.TestCase):
    def test_valid(self):
        spec_basic = StaticList(['1', '2', '3'], default='2')
        with self.subTest(spec=spec_basic):
            self.assertTrue('2' in spec_basic)
            self.assertFalse('10' in spec_basic)
            self.assertEqual(len(spec_basic), 3)

    def test_errors(self):
        with self.assertRaises(ValueError):
            StaticList(['1', '2', '3'], default='5')
        with self.assertRaises(ValueError):
            StaticList(['1', '2', '3'], defaultIndex=5)


class Test_StaticMap(unittest.TestCase):
    map_basic = {'1': 1, '2': 2, '3': 3}

    def test_valid(self):
        spec_basic = StaticMap(self.map_basic, defaultLabel='2')
        with self.subTest(spec=spec_basic):
            self.assertTrue('2' in spec_basic)
            self.assertTrue(2 in spec_basic.rlabels)
            self.assertFalse('5' in spec_basic)
            self.assertFalse(5 in spec_basic.rlabels)
            self.assertEqual(len(spec_basic), 3)

    def test_valid_wrappers(self):
        spec_basic_labels = StaticMapLabels(int, tuple(self.map_basic.keys()), defaultIndex=0)
        with self.subTest(spec=spec_basic_labels):
            self.assertTrue('2' in spec_basic_labels)
            self.assertTrue(2 in spec_basic_labels.rlabels)
            self.assertFalse('5' in spec_basic_labels)
            self.assertFalse(5 in spec_basic_labels.rlabels)
            self.assertTrue('1', spec_basic_labels.ldefault)
        spec_basic_values = StaticMapValues(str, tuple(self.map_basic.values()), defaultIndex=-1)
        with self.subTest(spec=spec_basic_values):
            self.assertTrue('2' in spec_basic_values)
            self.assertTrue(2 in spec_basic_values.rlabels)
            self.assertFalse('5' in spec_basic_values)
            self.assertFalse(5 in spec_basic_values.rlabels)
            self.assertTrue('3', spec_basic_values.ldefault)

    def test_errors(self):
        with self.assertRaises(ValueError):
            StaticMap(self.map_basic, defaultLabel='5')
        with self.assertRaises(ValueError):
            StaticMap(self.map_basic, defaultValue=5)
        with self.assertRaises(AssertionError):
            StaticMapLabels(str, tuple(self.map_basic.values()), defaultIndex=0)


class Test_Limit(unittest.TestCase):
    def test_int_bounded(self):
        lim_imin = LimitBounded(1, 10, fn=fn.valNumber, imin=True, imax=False)
        with self.subTest(limit=str(lim_imin)):
            self.assertTrue('1' in lim_imin)
            self.assertTrue('5' in lim_imin)
            self.assertFalse('10' in lim_imin)
        lim_imax = LimitBounded('1', '10', fn=fn.valNumber, imin=False, imax=True)
        with self.subTest(limit=str(lim_imax)):
            self.assertFalse('1' in lim_imax)
            self.assertTrue('5' in lim_imax)
            self.assertTrue('10' in lim_imax)
        lim_inone = LimitBounded('1', '10', fn=fn.valNumber, imin=False, imax=False, default='5')
        with self.subTest(limit=str(lim_inone)):
            self.assertFalse('1' in lim_inone)
            self.assertTrue('5' in lim_inone)
            self.assertFalse('10' in lim_inone)

    def test_int_infinite(self):
        lim_nomin = LimitUnbounded(None, 10, fn=fn.valNumber)
        with self.subTest(limit=str(lim_nomin)):
            self.assertTrue('-100' in lim_nomin)
            self.assertTrue('5' in lim_nomin)
            self.assertFalse('+100' in lim_nomin)
        lim_nomax = LimitUnbounded('1', None, fn=fn.valNumber)
        with self.subTest(limit=str(lim_nomax)):
            self.assertFalse('-100' in lim_nomax)
            self.assertTrue('5' in lim_nomax)
            self.assertTrue('+100' in lim_nomax)

    def test_errors(self):
        for cls in (LimitBounded, LimitUnbounded):
            with self.assertRaises(ValueError):
                cls('1', '10', fn=fn.valNumber, imin=False, imax=False)  # Default Default 0 not in range
            with self.assertRaises(ValueError):
                # Weirdness: Strange `fn`
                cls('x', 'xxx', fn=len, default=2)  # No default roundtrip: str(2) == '2'; len('2') == 1; 1 != 2


if __name__ == '__main__':
    import sys
    logs_lvl = logging.DEBUG if '-v' in sys.argv else logging.INFO
    logging.basicConfig(level=logs_lvl, format='%(levelname)5.5s:%(funcName)s: %(message)s', stream=sys.stderr)
    unittest.main()
