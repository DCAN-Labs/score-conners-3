# score-conners-3

## Usage

There are two ways to use this scoring system:

### 1. Single Record Processing (Legacy)

    ./score-conners-3.sh /path/to/parents/CSV/file age sex parent_or_teacher
    
    sex should be either "male" or "female" (without the quotes).
    age should be an integer, such as 10.
    parent_or_teacher should be either "parent" or "teacher" (without the quotes).

#### Example

    ./score-conners-3.sh /home/miran045/reine097/projects/score-conners-3/data/sample/inputdata_Conners3parent_female10.csv 10 female parent

### 2. Batch Processing (New)

For processing multiple records from a CSV file with `record_id`, `con3_p_dob` (date of birth), and response columns:

    python src/dcan/Score.py input_csv sex [options]

#### Options
- `sex`: Either "male" or "female" (required)
- `--parents_or_teacher`: Either "parent" or "teacher" (default: parent)
- `--assessment_date`: Assessment date in MM/DD/YY format (default: current date)
- `--output`: Output CSV file path (default: print to stdout)

#### Examples

Process a CSV file and save results:

    python src/dcan/Score.py /path/to/conners3parent.csv male --output results.csv

Process with female subjects and print to stdout:

    python src/dcan/Score.py /path/to/conners3parent.csv female

Specify custom assessment date:

    python src/dcan/Score.py /path/to/conners3parent.csv male --assessment_date "01/15/25" --output results.csv

#### Input CSV Format

The input CSV should contain:
- `record_id`: Unique identifier for each record
- `con3_p_dob`: Date of birth in MM/DD/YY format
- `con3_p_1` through `con3_p_110`: Response values for questions 1-110

#### Output Format

The output CSV contains:
- `record_id`: Original record identifier
- `age`: Calculated age at assessment
- `sex`: Subject sex
- `dob`: Date of birth
- `{AREA}_raw`: Raw scores for each assessment area (AG, EF, HY, IN, LP, PR)
- `{AREA}_t`: T-scores for each assessment area
- `PI_raw`, `NI_raw`: Raw scores for Positive/Negative Impression indices

#### Notes
- Ages 17-21 may have limited support depending on the assessment area
- Missing response values are automatically filled with 0
- Records with missing date of birth are skipped with a warning
