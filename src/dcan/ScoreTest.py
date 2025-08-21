import unittest
import pandas as pd
import sys
import os

# Add the project root to Python path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.dcan.Score import do_total_scoring, get_t_score_from_raw_score


class ScoreTest(unittest.TestCase):
    def test_do_total_scoring(self):
        parents_score_file = "data/sample/inputdata_conners3parent.csv"
        actual_results = do_total_scoring(parents_score_file, 9, "male", 'parent')
        expected_results = \
            {'LP': (7, 57), 'PR': (0, 44), 'IN': (4, 45), 'AG': (0, 43), 'HY': (1, 40), 'EF': (6, 48), 'PI': 1, 'NI': 3}
        expected_keys = expected_results.keys()
        self.assertEqual(len(expected_keys), len(actual_results.keys()))
        for key in expected_keys:
            self.assertEqual(expected_results[key], actual_results[key])

    def test_do_total_scoring_female_10(self):
        parents_score_file = "data/sample/inputdata_Conners3parent_female10.csv"
        actual_results = do_total_scoring(parents_score_file, 10, "female", 'parent')
        expected_results = {'LP': (10, 64), 'PR': (10, 90), 'IN': (21, 82), 'AG': (9, 81), 'HY': (12, 67),
                            'EF': (21, 90), 'PI': 0, 'NI': 5}
        # IN (21, 82), HY (12, 67), LP (10, 64), EF (21, 90), AG (9, 81), PR (10, 90)
        expected_keys = expected_results.keys()
        self.assertEqual(len(expected_keys), len(actual_results.keys()))
        for key in expected_keys:
            self.assertEqual(expected_results[key], actual_results[key])

    def test_do_total_scoring_teacher_female_10(self):
        parents_score_file = "data/sample/sub1000701_inputdata_teacher_female_10.csv"
        actual_results = do_total_scoring(parents_score_file, 10, "female", 'teacher')
        # (IN: 2, 45) (HY: 2, 45) (LE: 4, 44) (AG: 1, 50) (PR: 0, 44)
        expected_results = \
            {'IN': (3, 47), 'HY': (2, 45), 'LE': (3, 43), 'AG': (0, 45), 'PR': (0, 44), 'PI': 2, 'NI': 0}
        expected_keys = expected_results.keys()
        self.assertEqual(len(expected_keys), len(actual_results.keys()))
        for key in expected_keys:
            self.assertEqual(expected_results[key], actual_results[key])

    def test_do_total_scoring_teacher_male_9(self):
        parents_score_file = "data/sample/sub1000201_inputdata_teacher_9_male.csv"
        actual_results = do_total_scoring(parents_score_file, 9, "male", 'teacher')
        # (IN: 0, 42) (HY 0, 41) (LE: 5, 45) (AG: 0, 44) (PR: 0, 43)
        expected_results = \
            {'IN': (0, 42), 'HY': (0, 41), 'LE': (5, 45), 'AG': (0, 44), 'PR': (0, 43), 'PI': 4, 'NI': 0}
        expected_keys = expected_results.keys()
        self.assertEqual(len(expected_keys), len(actual_results.keys()))
        for key in expected_keys:
            self.assertEqual(expected_results[key], actual_results[key])

    def test_do_total_scoring_male_10(self):
        parents_score_file = "data/sample/inputdata_Conners3parent_male10.csv"
        actual_results = do_total_scoring(parents_score_file, 10, "male", 'parent')
        expected_results = \
            {'LP': (10, 64), 'IN': (19, 75), 'AG': (5, 63), 'HY': (29, 89), 'EF': (13, 61), 'PR': (0, 43), 'PI': 0, 'NI': 3}
        # SUB-10016-01: {'LP': (10, 64), 'IN': (19, 75), 'AG': (5, 63), 'HY': (29, 89), 'EF': (13, 61), 'PR': (0, 43)}
        expected_keys = expected_results.keys()
        self.assertEqual(len(expected_keys), len(actual_results.keys()))
        for key in expected_keys:
            self.assertEqual(expected_results[key], actual_results[key])

    def test_get_t_score_from_raw_score_high(self):
        raw_score = 23
        csv_file = 'data/constant/parent/male_lp.csv'
        df = pd.read_csv(csv_file)
        age = 9
        age_str = str(age)
        column_0_name = 'Unnamed: 0'
        age_column = df[[column_0_name, age_str]]
        scores_df = age_column.rename(columns={"Unnamed: 0": "t-score", age_str: "raw score"})
        t_score = get_t_score_from_raw_score(raw_score, scores_df)
        self.assertEqual(90, t_score)

    def test_get_t_score_from_raw_score_low(self):
        raw_score = 0
        csv_file = 'data/constant/parent/male_lp.csv'
        df = pd.read_csv(csv_file)
        age = 9
        age_str = str(age)
        column_0_name = 'Unnamed: 0'
        age_column = df[[column_0_name, age_str]]
        scores_df = age_column.rename(columns={"Unnamed: 0": "t-score", age_str: "raw score"})
        t_score = get_t_score_from_raw_score(raw_score, scores_df)
        self.assertEqual(40, t_score)


if __name__ == '__main__':
    unittest.main()
