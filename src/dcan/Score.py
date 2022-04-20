import math
from collections import Counter
from os.path import exists

import pandas as pd

QUESTION_OFFSET = 5


def do_total_scoring(parents_score_file, age, sex, parents_or_teacher):
    # TODO Implement using teacher_score_file
    lookup_table_file = f"data/constant/scoringsheet_conners3{parents_or_teacher}.csv"
    column_name_to_score = do_scoring(parents_score_file, lookup_table_file)
    t_score = get_t_score(age, sex, column_name_to_score, parents_or_teacher)

    return t_score


def get_area_scores(question_number, scores_df, lookup_df):
    score = scores_df.iloc[0][question_number]
    looked_up_score = lookup_df.iloc[question_number][score + 1]
    area_name_to_score = {}
    for area_col in range(QUESTION_OFFSET, 8):
        area = lookup_df.iloc[question_number][area_col]
        area = area.strip()
        if area:
            area_name_to_score[area] = looked_up_score

    return area_name_to_score


# TODO Implement for teacher_score_file
def do_scoring(scores_file, lookup_table_file):
    scores_df = pd.read_csv(scores_file)
    scores_df = scores_df.iloc[:, QUESTION_OFFSET:]
    question_count = scores_df.size
    area_name_to_score = {}
    lookup_df = pd.read_csv(lookup_table_file)
    lookup_df.fillna('', inplace=True)

    area_scores = \
        [get_area_scores(question_number, scores_df, lookup_df) for question_number in range(question_count)]
    for area_score in area_scores:
        c_dict = Counter(area_name_to_score) + Counter(area_score)
        area_name_to_score = c_dict

    areas = ['AG', 'EF', 'HY', 'IN', 'LP', 'PR']
    for area in areas:
        if area not in area_name_to_score.keys():
            area_name_to_score[area] = 0

    return area_name_to_score


def get_t_score(age, gender, column_name_to_score, parents_or_teacher):
    result = {}
    for key in column_name_to_score.keys():
        csv_file = f'data/constant/{parents_or_teacher}/{gender}_{key.lower()}.csv'
        if not exists(csv_file):
            continue
        df = pd.read_csv(csv_file)
        age_str = str(age)
        column_0_name = 'Unnamed: 0'
        age_column = df[[column_0_name, age_str]]
        scores_df = age_column.rename(columns={"Unnamed: 0": "t-score", age_str: "raw score"})
        raw_score = column_name_to_score[key]
        t_score = get_t_score_from_raw_score(raw_score, scores_df)
        result[key] = (raw_score, t_score)
    return result


def get_t_score_from_raw_score(raw_score, scores_df):
    row = None
    found = False
    for index, row in scores_df.iterrows():
        if math.isnan(row['raw score']):
            continue
        if int(row['raw score']) <= raw_score:
            found = True
            break
    if found:
        t_score = int(row['t-score'])
    else:
        t_score = 40
    return t_score
