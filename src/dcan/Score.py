import math
from collections import Counter
from os.path import exists
from datetime import datetime
import tempfile
import os

import pandas as pd
from pandas import DataFrame, concat

AREA_COL_END = 8

AREA_COL_START = 5

QUESTION_OFFSET = 4


def do_total_scoring(parents_score_file, age, sex, parents_or_teacher):
    lookup_table_file = f"data/constant/scoringsheet_conners3{parents_or_teacher}.csv"
    column_name_to_score = do_scoring(parents_score_file, lookup_table_file)
    t_score = get_t_score(age, sex, column_name_to_score, parents_or_teacher)

    return t_score


def get_area_scores(question_number, scores_df, lookup_df):
    score = scores_df.iloc[0, question_number]
    looked_up_score = lookup_df.iloc[question_number, score + 1]
    area_name_to_score = {}
    for area_col in range(AREA_COL_START, AREA_COL_END):
        area = lookup_df.iloc[question_number, area_col]
        if area:
            area_name_to_score[area] = looked_up_score

    return area_name_to_score


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

    # Areas PI and NI -- only raw score -- no t-score
    if 'parent' in lookup_table_file:
        areas = ['AG', 'EF', 'HY', 'IN', 'LP', 'PR', 'PI', 'NI']
    else:
        areas = ['AG', 'HY', 'IN', 'LE', 'PR', 'PI', 'NI']
    for area in areas:
        if area not in area_name_to_score.keys():
            area_name_to_score[area] = 0

    return area_name_to_score


def get_t_score(age, gender, column_name_to_score, parents_or_teacher):
    result = {}
    for key in column_name_to_score.keys():
        if key not in ['PI', 'NI']:
            csv_file = f'data/constant/{parents_or_teacher}/{gender}_{key.lower()}.csv'
            if not exists(csv_file):
                continue
            df = pd.read_csv(csv_file)
            age_str = str(age)
            column_0_name = 'T'
            if age_str not in df.columns:
                print(f"Warning: Age {age} not supported for area {key}")
                continue
            age_column = df[[column_0_name, age_str]]
            scores_df = age_column.rename(columns={"T": "t-score", age_str: "raw score"})
            index = contains_multiple_raw_scores(scores_df)
            while index:
                scores_df = split_multiple_raw_score(scores_df, index)
                index = contains_multiple_raw_scores(scores_df)
            raw_score = column_name_to_score[key]
            t_score = get_t_score_from_raw_score(raw_score, scores_df)
            result[key] = (int(raw_score), int(t_score))
        else:
            raw_score = column_name_to_score[key]
            result[key] = raw_score

    return result


def split_multiple_raw_score(df, index):
    row = df.iloc[index]
    raw_score_str = row['raw score']
    parts = raw_score_str.split('-')
    if len(parts) != 2:
        return df
    lower_raw_score, upper_raw_score = parts
    try:
        lower_val = int(lower_raw_score)
        upper_val = int(upper_raw_score)
    except ValueError:
        return df
    
    t_score = row['t-score']
    lower_line = DataFrame({"t-score": int(t_score), "raw score": lower_val}, index=[index + 1])
    upper_line = DataFrame({"t-score": int(t_score), "raw score": upper_val}, index=[index])
    df2 = concat([df.iloc[:index], upper_line, lower_line, df.iloc[index + 1:]]).reset_index(drop=True)

    return df2


def contains_multiple_raw_scores(df):
    df = df.reset_index()
    for index, row in df.iterrows():
        raw_score = row['raw score']
        if isinstance(raw_score, str) and '-' in raw_score:
            return index
    return None

def get_t_score_from_raw_score(raw_score, scores_df):
    row = None
    found = False
    scores_df = scores_df.astype('float64')
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


def calculate_age_from_dob(dob_str, assessment_date=None):
    if assessment_date is None:
        assessment_date = datetime.now()
    elif isinstance(assessment_date, str):
        assessment_date = datetime.strptime(assessment_date, '%m/%d/%y')
    
    dob = datetime.strptime(dob_str, '%m/%d/%y')
    age = assessment_date.year - dob.year
    if (assessment_date.month, assessment_date.day) < (dob.month, dob.day):
        age -= 1
    return age


def process_batch_scores(input_csv_path, sex, parents_or_teacher='parent', assessment_date=None, output_csv_path=None):
    df = pd.read_csv(input_csv_path)
    results = []
    
    for index, row in df.iterrows():
        record_id = row['record_id']
        dob = row['con3_p_dob']
        
        if pd.isna(dob):
            print(f"Warning: Skipping record {record_id} - missing date of birth")
            continue
            
        age = calculate_age_from_dob(dob, assessment_date)
        
        question_responses = row.iloc[5:115]
        question_responses = question_responses.fillna(0)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_df = pd.DataFrame([question_responses.values])
            temp_df.to_csv(temp_file.name, index=False, header=False)
            temp_file_path = temp_file.name
        
        try:
            t_scores = do_total_scoring(temp_file_path, age, sex, parents_or_teacher)
            
            result_row = {
                'record_id': record_id,
                'age': age,
                'sex': sex,
                'dob': dob
            }
            
            for area, scores in t_scores.items():
                if isinstance(scores, tuple):
                    result_row[f'{area}_raw'] = scores[0]
                    result_row[f'{area}_t'] = scores[1]
                else:
                    result_row[f'{area}_raw'] = scores
                    
            results.append(result_row)
            
        except Exception as e:
            print(f"Error processing record {record_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            os.unlink(temp_file_path)
    
    results_df = pd.DataFrame(results)
    
    if output_csv_path:
        results_df.to_csv(output_csv_path, index=False)
        print(f"Results saved to {output_csv_path}")
    
    return results_df


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Conners-3 scores for multiple subjects')
    parser.add_argument('input_csv', help='Path to input CSV file with subject data')
    parser.add_argument('sex', choices=['male', 'female'], help='Sex of subjects (all subjects must be same sex)')
    parser.add_argument('--parents_or_teacher', choices=['parent', 'teacher'], default='parent',
                        help='Type of assessment (default: parent)')
    parser.add_argument('--assessment_date', help='Assessment date in MM/DD/YY format (default: current date)')
    parser.add_argument('--output', help='Output CSV file path (default: print to stdout)')
    
    args = parser.parse_args()
    
    results_df = process_batch_scores(
        args.input_csv, 
        args.sex, 
        args.parents_or_teacher,
        args.assessment_date,
        args.output
    )
    
    if not args.output:
        print(results_df.to_csv(index=False))


if __name__ == '__main__':
    main()
