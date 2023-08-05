import csv
import os
import unittest

from KaggleToDatabricks import TransformDataset

TD = TransformDataset.TransformDataset
test_file = '/dbfs/FileStore/Kaggle_Datasets/test.csv'
rows = [
    ['0a', '0b', '0c'],
    ['1a', '1b', '1c'],
]


class TestTransformDataset(unittest.TestCase):

    def setUp(self):
        """
        Creating dummy csv file to test on
        """
        with open(test_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)

    def tearDown(self):
        """
        clearing dummy csv file after test
        """
        os.remove(test_file)

    def test_df_from_dataset(self):
        """
        testing df_from_dataset using dummy csv file created from test_file and rows variables
        """
        result = TD.df_from_dataset(self, "/dbfs/FileStore/Kaggle_Datasets", "test.csv")
        self.assertIsInstance(result, pd.DataFrame, "hej hej")

    if __name__ == '__main__':
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
