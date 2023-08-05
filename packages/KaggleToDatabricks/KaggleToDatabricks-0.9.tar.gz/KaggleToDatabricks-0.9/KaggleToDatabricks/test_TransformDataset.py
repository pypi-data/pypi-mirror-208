import unittest
import TransformDataset
import csv
import os
import pandas as pd

test_file = 'test.csv'
rows = [
    ['0a', '0b', '0c'],
    ['1a', '1b', '1c'],
]

class TestTransformDataset(unittest.TestCase):


    def setUp(self):
        with open(test_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)

    def tearDown(self):
        os.remove(test_file)

    def test_df_from_dataset(self):

        result = TransformDataset.df_from_dataset("",test_file)
        self.assertEqual(type(result), type(pd.DataFrame))


    if __name__ == '__main__':
        unittest.main()

