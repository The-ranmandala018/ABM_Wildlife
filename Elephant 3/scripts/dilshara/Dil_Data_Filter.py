import pandas as pd
import os
import glob

def filter_by_minute(path):

    # Read the CSV file
    df = pd.read_csv(path)

    # Combine Date and Time into a single datetime column for easier processing
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%m/%d/%Y %I:%M:%S %p')

    # Filter rows where seconds are '00'
    df_filtered = df[df['DateTime'].dt.second == 0]

    # Sort the filtered DataFrame by DateTime to ensure chronological order
    df_filtered = df_filtered.sort_values(by='DateTime')

    # Drop the temporary DateTime column and keep only the original columns
    df_filtered = df_filtered[['Longitude', 'Latitude', 'tag-local-identifier', 'Date', 'Time']]

    # Save the filtered and sorted DataFrame to an Excel file
    output_path = 'output_sorted.csv'
    df_filtered.to_csv(output_path, index=False)
    print(f"Saved {output_path} with {len(df_filtered)} rows")

def filter_by_five_minutes(df, date_col='Date', time_col='Time', output_path='filtered_by_five_minutes.csv'):

    try:
        # Create a copy of the DataFrame to avoid modifying the original
        df = df.copy()
        
        # Combine Date and Time into a single datetime column
        df['DateTime'] = pd.to_datetime(df[date_col] + ' ' + df[time_col], format='%m/%d/%Y %I:%M:%S %p')
        
        # Filter rows where seconds are '00' and minutes are divisible by 5
        df_filtered = df[(df['DateTime'].dt.second == 0) & (df['DateTime'].dt.minute % 5 == 0)]
        
        # Sort the filtered DataFrame by DateTime
        df_filtered = df_filtered.sort_values(by='DateTime')
        
        # Keep only the original columns
        original_columns = [col for col in df.columns if col != 'DateTime']
        df_filtered = df_filtered[original_columns]
        
        # Save the filtered and sorted DataFrame to a CSV file
        df_filtered.to_csv(output_path, index=False)
        print(f"Saved {output_path} with {len(df_filtered)} rows")
        
        return df_filtered
    
    except ValueError as e:
        print(f"Error processing datetime: {e}. Ensure 'Date' and 'Time' columns are in 'MM/DD/YYYY' and 'HH:MM:SS AM/PM' format.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    path_pattern = "../data/SM/*.csv"
    
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
                df = pd.read_csv(csv_file)
                
                # Generate output path by appending '_filtered' to the original filename
                base_name = os.path.basename(csv_file).replace('.csv', '')
                output_path = f"../data/SM/{base_name}_filtered.csv"
                
                # Apply the filtering function
                filtered_df = filter_by_five_minutes(df, output_path=output_path)
                
                if filtered_df is not None:
                    print(f"Successfully processed {csv_file}")
                else:
                    print(f"Failed to process {csv_file}")
                    
            except FileNotFoundError:
                print(f"File not found: {csv_file}")
            except Exception as e:
                print(f"Error processing {csv_file}: {e}")
    
    # try:
    #     df = pd.read_csv(path)
        
    #     # Apply the filtering function
    #     filtered_df = filter_by_five_minutes(df)
        
    #     if filtered_df is not None:
    #         print("Filtering completed successfully.")
    #     else:
    #         print("Filtering failed.")
            
    # except FileNotFoundError:
    #     print(f"File not found: {path}")



    # # Rename columns
    # df = df.rename(columns={'location-long': 'Longitude', 'location-lat': 'Latitude'})
    # unique_tags = df['tag-local-identifier'].unique()

    # results = []
    # for tag in unique_tags:
    #     shape = read_csv(input_csv1, tag)
    #     if shape is not None:
    #         print(f"{tag} : {shape}")
    #         results.append({'Tag': tag, 'Shape': str(shape)})
    
    # # Save to CSV
    # if results:
    #     output_df = pd.DataFrame(results)
    #     output_csv = "tags_and_shapes4.csv"
    #     output_df.to_csv(output_csv, index=False)
    #     print(f"\nResults saved to '{output_csv}'")
    # else:
    #     print("No results to save.")