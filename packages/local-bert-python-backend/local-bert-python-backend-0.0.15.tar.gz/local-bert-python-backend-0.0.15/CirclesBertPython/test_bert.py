import unittest
import pandas as pd
import numpy as np
from bert import BertCircles


class TestBertCircles(unittest.TestCase):
    def setUp(self):
        self.bert = BertCircles()
        self.csv_table = pd.DataFrame({'field2': ['data science', 'software engineering', 'database management'],
                                       'field1': [1, 2, 3]})

    def test_get_sentence_embedding(self):
        sentence = 'This is a sample sentence for testing'
        embedding = self.bert.get_sentence_embedding(sentence)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (1, 768))

    def test_classify(self):
        # Test when best match is the first row in csv_table
        result = self.bert.classify('field1', 'field2', self.csv_table, None, 'Data Scientist',self.csv_table)
        self.assertEqual(result, ['data science', 1])

        # Test when best match is the second row in csv_table
        result = self.bert.classify('field1', 'field2', self.csv_table, None, 'Software Engineering Job',self.csv_table)
        self.assertEqual(result, ['software engineering', 2])

        # Test when best match is the third row in csv_table
        result = self.bert.classify('field1', 'field2', self.csv_table, None, 'Database Administrator', self.csv_table)
        self.assertEqual(result, ['database management', 3])


if __name__ == '__main__':
    unittest.main()
