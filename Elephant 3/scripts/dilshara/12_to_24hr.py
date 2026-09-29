import pandas as pd
from datetime import datetime
import glob
import os

def convert_time_to_24hr(csv_file, time_column, output_file=None):
    """
    Convert time in AM/PM format (e.g., '3:05:00 AM') to 24-hour format in a CSV file,
    renaming the original time column to 'timeAPM' and creating a new 'Time' column.
    
    Parameters:
    - csv_file (str): Path to the input CSV file.
    - time_column (str): Name of the column containing time in AM/PM format.
    - output_file (str, optional): Path to save the modified CSV file. If None, overwrites the input file.
    
    Returns:
    - pd.DataFrame or None: The modified DataFrame, or None if an error occurs.
    """
    try:
        # Verify input file exists and is accessible
        if not os.path.isfile(csv_file):
            raise FileNotFoundError(f"Input file '{csv_file}' does not exist.")
        
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Ensure the time column exists
        if time_column not in df.columns:
            raise ValueError(f"Column '{time_column}' not found in the CSV file.")
        
        # Function to convert single time string
        def to_24hr(time_str):
            # Handle float values (e.g., NaN)
            if isinstance(time_str, float):
                print(f"Warning: Found float value '{time_str}' in time column. Returning as is.")
                return time_str
            try:
                # Parse AM/PM time with seconds (e.g., "3:05:00 AM")
                time_obj = datetime.strptime(time_str.strip(), "%I:%M:%S %p")
                # Convert to 24-hour format with seconds
                return time_obj.strftime("%H:%M:%S")
            except ValueError as e:
                print(f"Warning: Could not parse time '{time_str}'. Error: {e}")
                return time_str  # Return original value if parsing fails
        
        # Rename the original time column to 'timeAPM'
        df = df.rename(columns={time_column: 'timeAPM'})
        
        # Create new 'Time' column with 24-hour format
        df['Time'] = df['timeAPM'].apply(to_24hr)
        
        # Save the modified DataFrame
        output_file = output_file or csv_file
        df.to_csv(output_file, index=False)
        print(f"CSV file saved to: {output_file}")
        
        return df
    
    except PermissionError as e:
        print(f"Error processing {csv_file}: Permission error: {e}. Check file/directory permissions.")
        return None
    except FileNotFoundError as e:
        print(f"Error processing {csv_file}: {e}")
        return None
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")
        return None



# Example usage
if __name__ == "__main__":

    class_names = ["AF", "AM", "JM", "SF", "SM"]
    
    for class_name in class_names:
        
        path_pattern = f"../../data/{class_name}/*.csv"
        base_output_path = f"../../data/{class_name}"
        
        os.makedirs(base_output_path, exist_ok=True) 
        
        # Get list of all CSV files matching the pattern
        csv_files = glob.glob(path_pattern)
        
        if not csv_files:
            print(f"No CSV files found in {path_pattern}")
        else:
            print(f"Found {len(csv_files)} CSV files to process")
            
            # Process each CSV file
            for csv_file in csv_files:
                try:
                    # Read the CSV file
                    # print(csv_file)
                    # df = pd.read_csv(csv_file)
                    
                    # Generate output path by appending '_filtered' to the original filename
                    base_name = os.path.basename(csv_file).replace('.csv', '')
                    output_path = f"{base_output_path}/{base_name}_time.csv"
                    filtered_df = convert_time_to_24hr(csv_file, "Time", output_path)

                    if filtered_df is not None:
                        print(f"Successfully processed {csv_file}")
                    else:
                        print(f"Failed to process {csv_file}")
                        
                except FileNotFoundError:
                    print(f"File not found: {csv_file}")
                except Exception as e:
                    print(f"Error processing {csv_file}: {e}")