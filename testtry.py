import unittest
import trytest


class TestCalc(unittest.TestCase):

    def test_add(self):
        self.assertEqual(trytest.add(10, 5), 15)
        self.assertEqual(trytest.add(-1, 1), 0)
        self.assertEqual(trytest.add(-1, -1), -2)

    def test_subtract(self):
        self.assertEqual(trytest.subtract(10, 5), 5)
        self.assertEqual(trytest.subtract(-1, 1), -2)
        self.assertEqual(trytest.subtract(-1, -1), 0)

    def test_multiply(self):
        self.assertEqual(trytest.multiply(10, 5), 50)
        self.assertEqual(trytest.multiply(-1, 1), -1)
        self.assertEqual(trytest.multiply(-1, -1), 1)

    def test_divide(self):
        self.assertEqual(trytest.divide(10, 5), 2)
        self.assertEqual(trytest.divide(-1, 1), -1)
        self.assertEqual(trytest.divide(-1, -1), 1)
        self.assertEqual(trytest.divide(5, 2), 2.5)

        with self.assertRaises(ValueError):
            trytest.divide(10, 0)


if __name__ == '__main__':
    unittest.main()