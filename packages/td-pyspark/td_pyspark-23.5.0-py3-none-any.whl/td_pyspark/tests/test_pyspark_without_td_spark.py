import td_pyspark
import unittest

class TDPySparkWithoutTDSparkTest(unittest.TestCase):
    def test_default_jar_path(self):
        jar_path = td_pyspark.TDSparkContextBuilder.default_jar_path()
        self.assertTrue(jar_path.endswith('td-spark-assembly.jar'))

if __name__ == '__main__':
    unittest.main()