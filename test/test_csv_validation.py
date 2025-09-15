import csv
import unittest
from io import StringIO


class TestCSVValidation(unittest.TestCase):
    
    def test_csv_has_consistent_column_count(self):
        """Test that all rows in a CSV file have the same number of columns."""
        
        def validate_csv_columns(csv_file_path):
            """
            Check that each row in a CSV file has the same number of columns.
            
            Args:
                csv_file_path (str): Path to the CSV file
                
            Returns:
                bool: True if all rows have same column count, False otherwise
                
            Raises:
                ValueError: If rows have inconsistent column counts
            """
            with open(csv_file_path, 'r', newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if not rows:
                    return True  # Empty file is valid
                
                # Get expected column count from first non-empty row
                expected_cols = None
                for i, row in enumerate(rows):
                    if row:  # Skip empty rows
                        expected_cols = len(row)
                        break
                
                if expected_cols is None:
                    return True  # All rows empty
                
                # Check all rows have same column count
                for i, row in enumerate(rows):
                    if not row:  # Skip empty rows
                        continue
                    if len(row) != expected_cols:
                        raise ValueError(
                            f"Row {i+1} has {len(row)} columns, expected {expected_cols}"
                        )
                        
                return True
        
        # Test with the actual CSV file
        csv_file = "/data/constant/parent/female_in.csv"
        self.assertTrue(validate_csv_columns(csv_file))
    
    def test_csv_validation_with_inconsistent_columns(self):
        """Test that validation fails for CSV with inconsistent columns."""
        
        def validate_csv_columns(csv_content):
            reader = csv.reader(StringIO(csv_content))
            rows = list(reader)
            
            if not rows:
                return True
            
            expected_cols = len(rows[0])
            for i, row in enumerate(rows):
                if len(row) != expected_cols:
                    raise ValueError(
                        f"Row {i+1} has {len(row)} columns, expected {expected_cols}"
                    )
            return True
        
        # Test data with inconsistent columns
        inconsistent_csv = "col1,col2,col3\nval1,val2,val3\nval4,val5\nval6,val7,val8"
        
        with self.assertRaises(ValueError) as context:
            validate_csv_columns(inconsistent_csv)
        
        self.assertIn("Row 3 has 2 columns, expected 3", str(context.exception))
    
    def test_csv_validation_with_consistent_columns(self):
        """Test that validation passes for CSV with consistent columns."""
        
        def validate_csv_columns(csv_content):
            reader = csv.reader(StringIO(csv_content))
            rows = list(reader)
            
            if not rows:
                return True
            
            expected_cols = len(rows[0])
            for i, row in enumerate(rows):
                if len(row) != expected_cols:
                    raise ValueError(
                        f"Row {i+1} has {len(row)} columns, expected {expected_cols}"
                    )
            return True
        
        # Test data with consistent columns
        consistent_csv = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6\nval7,val8,val9"
        
        self.assertTrue(validate_csv_columns(consistent_csv))
    
    def test_find_trend_violations(self):
        """Find and report all trend violations in normative tables."""
        
        def find_trend_violations(csv_file_path):
            """
            Find all places where values increase when T-score decreases.
            
            Args:
                csv_file_path (str): Path to the CSV file
                
            Returns:
                list: List of violation descriptions
            """
            violations = []
            
            with open(csv_file_path, 'r', newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if len(rows) < 2:
                    return violations
                
                # Get column headers
                headers = rows[0] if rows else []
                
                # Skip header row and convert numeric values
                data_rows = []
                for row_idx, row in enumerate(rows[1:], 2):  # Start from row 2 (1-indexed)
                    if not row or not row[0]:
                        continue
                    try:
                        t_score = float(row[0])
                        numeric_row = [t_score, row_idx]  # Include original row number
                        for cell in row[1:]:
                            if cell.strip():
                                try:
                                    numeric_row.append(float(cell))
                                except ValueError:
                                    numeric_row.append(None)
                            else:
                                numeric_row.append(None)
                        data_rows.append(numeric_row)
                    except ValueError:
                        continue
                
                if len(data_rows) < 2:
                    return violations
                
                # Sort by T-score descending (highest first)
                data_rows.sort(key=lambda x: x[0], reverse=True)
                
                # Check each column for violations
                num_cols = len(data_rows[0]) - 1  # Subtract 1 for row number
                for col_idx in range(2, num_cols + 1):  # Skip T-score and row number
                    col_name = headers[col_idx - 2] if col_idx - 2 < len(headers) else f"Column_{col_idx-1}"
                    
                    # Get non-None values with their T-scores and row numbers
                    col_data = []
                    for row in data_rows:
                        if col_idx < len(row) and row[col_idx] is not None:
                            col_data.append((row[0], row[col_idx], row[1]))  # (t_score, value, row_num)
                    
                    if len(col_data) < 2:
                        continue
                    
                    # Find violations
                    for i in range(len(col_data) - 1):
                        curr_t, curr_val, curr_row = col_data[i]
                        next_t, next_val, next_row = col_data[i + 1]
                        
                        if next_val > curr_val:  # Value increased as T-score decreased
                            violations.append(
                                f"{col_name}: T={next_t} (row {next_row}) has value {next_val} > "
                                f"T={curr_t} (row {curr_row}) value {curr_val}"
                            )
            
            return violations
        
        # Check both files for violations
        female_in_file = "/data/constant/parent/female_in.csv"
        female_ag_file = "/data/constant/parent/female_ag.csv"
        
        print(f"\n=== Violations in female_in.csv ===")
        in_violations = find_trend_violations(female_in_file)
        for violation in in_violations[:20]:  # Show first 20
            print(violation)
        if len(in_violations) > 20:
            print(f"... and {len(in_violations) - 20} more violations")
        print(f"Total violations: {len(in_violations)}")
        
        print(f"\n=== Violations in female_ag.csv ===")
        ag_violations = find_trend_violations(female_ag_file)
        for violation in ag_violations[:20]:  # Show first 20
            print(violation)
        if len(ag_violations) > 20:
            print(f"... and {len(ag_violations) - 20} more violations")
        print(f"Total violations: {len(ag_violations)}")
        
        # This test always passes - it's just for reporting
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
