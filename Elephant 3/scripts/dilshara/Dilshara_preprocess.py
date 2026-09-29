import pandas as pd
import os
import matplotlib.pyplot as plt
import glob

def split_dataset_by_tag(input_csv_path, output_base_dir):
    # Read the input CSV file with only required columns
    df = pd.read_csv(input_csv_path, usecols=['tag-local-identifier', 'location-long', 'location-lat', 'timestamp'])
    
    # Rename columns
    df = df.rename(columns={'location-long': 'Longitude', 'location-lat': 'Latitude'})
    
    # Convert timestamp to datetime, handling ISO8601-like format with milliseconds
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create Date and Time columns in the desired format
    df['Date'] = df['timestamp'].dt.strftime('%m/%d/%Y')
    df['Time'] = df['timestamp'].dt.strftime('%I:%M:%S %p')
    
    # Drop the original timestamp column
    df = df.drop('timestamp', axis=1)
    
    # Get unique tag-local-identifiers
    unique_tags = df['tag-local-identifier'].unique()
    
    # Create output base directory if it doesn't exist
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Process each tag
    for tag in unique_tags:
        # Create a folder for the tag
        tag_folder = os.path.join(output_base_dir, str(tag))

        # Filter data for the current tag
        tag_data = df[df['tag-local-identifier'] == tag]

        if os.path.exists(tag_folder):
            csv_file_path = f'{output_base_dir}/{tag}/{tag}_data.csv'
            # df_before = pd.read_csv(csv_file_path)
            tag_data.to_csv(csv_file_path, mode='a', header=False, index=False)
            print(f"Added dataset for tag {tag}")

        else:
            os.makedirs(tag_folder, exist_ok=True)
        
            # Define output file path
            output_file = os.path.join(tag_folder, f"{tag}_data.csv")
            
            # Save the filtered data to CSV
            tag_data.to_csv(output_file, index=False)
            print(f"Created dataset for tag {tag} at {output_file}")

def read_csv(input_csv_path, id):
    df = pd.read_csv(input_csv_path)
    # information = df.info()
    # shape_information = df.shape
    # df_unique = df[df['tag-local-identifier'] == id]
    df.info()

    
    # print(unique_categories.head())
    # unique_categories1 = df['individual-local-identifier'].unique()

    # print(shape_information)
    # print(df_unique.head())
    # return df_unique.shape[0]
    # print(unique_categories1)

def plot_null_perday(csv_path, output_dir):
    
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_path)
        
        # Check if required columns exist
        required_columns = ['Longitude', 'Date']
        if not all(col in df.columns for col in required_columns):
            print(f"Skipping {csv_path}: Missing required columns {required_columns}")
            return
        
        # Ensure DataFrame is sorted by 'Date' for consistent ordering
        df = df.sort_values(by='Date')
        
        # Get unique days
        days = df['Date'].unique()
        
        # Iterate through each day
        for day in days:
            # Filter data for the current day
            day_mask = df['Date'] == day
            day_data = df[day_mask]
            
            # Get the number of data points for the day
            data_per_day = day_data.shape[0]
            
            # Count null values in 'Longitude' for the day
            null_count = day_data['Longitude'].isna().sum()
            
            # Only plot if there are 2 or more null values
            # Create a list of 1s (null) and 0s (non-null) for the 'Longitude' column
            null_status = day_data['Longitude'].isna().astype(int)  # 1 for null, 0 for non-null
            
            # Create x-axis points (indices of data points for the day)
            x_points = range(data_per_day)
            
            # Set up the plot for the current day
            plt.figure(figsize=(8, 5))
            plt.scatter(x_points, null_status, label=f'Day: {day}', alpha=0.6, s=100)
            
            # Customize the plot
            plt.xlabel('Data Point Index in Day')
            plt.ylabel('Null Status (1 = Null, 0 = Non-Null)')
            plt.title(f'Null vs Non-Null Longitude Values for {day} ({os.path.basename(csv_path)})')
            plt.yticks([0, 1], ['Non-Null', 'Null'])
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Generate output filename with the date and file identifier
            date_str = str(day).replace('/', '-')  # Replace any invalid characters for filenames
            file_prefix = os.path.basename(csv_path).replace('.csv', '')
            day_output_path = os.path.join(output_dir, f'null_plot_{file_prefix}_{date_str}.png')
            
            # Save the plot
            plt.savefig(day_output_path, bbox_inches='tight')
            plt.close()
            print(f"Saved plot: {day_output_path}")
                
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
    except Exception as e:
        print(f"Error processing {csv_path}: {e}")

def save_null_locations_perday(csv_path, output_dir):
    """
    Save CSV files containing 'Date' and 'Time' for rows with null 'Longitude' values for each day.
    
    Parameters:
    - csv_path: str, path to the input CSV file
    - output_dir: str, directory to save the output CSV files
    """
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_path)
        
        # Check if required columns exist
        required_columns = ['Longitude', 'Date', 'Time']
        if not all(col in df.columns for col in required_columns):
            print(f"Skipping {csv_path}: Missing required columns {required_columns}")
            return
        
        # Ensure DataFrame is sorted by 'Date' for consistent ordering
        df = df.sort_values(by='Date')
        
        # Get unique days
        days = df['Date'].unique()
        
        # Iterate through each day
        for day in days:
            # Filter data for the current day
            day_mask = df['Date'] == day
            day_data = df[day_mask]
            
            # Filter rows with null 'Longitude' values
            null_data = day_data[day_data['Longitude'].isna()]
            
            # Only save if there are null values
            if not null_data.empty:
                # Select only 'Date' and 'Time' columns
                null_data = null_data[['Date', 'Time']]
                
                # Generate output filename with the date and file identifier
                date_str = str(day).replace('/', '-')  # Replace any invalid characters for filenames
                file_prefix = os.path.basename(csv_path).replace('.csv', '')
                day_output_path = os.path.join(output_dir, f'null_locations_{file_prefix}_{date_str}.csv')
                
                # Save the null data to a CSV file
                null_data.to_csv(day_output_path, index=False)
                print(f"Saved CSV: {day_output_path} with {len(null_data)} rows")
                
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
    except Exception as e:
        print(f"Error processing {csv_path}: {e}")

# Example usage
if __name__ == "__main__":

    # input_csv1 = "../data/Collective_baboons/Collective movement in wild baboons-gps-4of4.csv"  # Replace with your CSV file path
    # # input_csv2 = "../data/Collective_baboons/Collective movement in wild baboons-gps-2of4.csv"  # Replace with your CSV file path
    # # input_csv3 = "../data/Collective_baboons/Collective movement in wild baboons-gps-3of4.csv"  # Replace with your CSV file path
    # # input_csv4 = "../data/Collective_baboons/Collective movement in wild baboons-gps-4of4.csv"  # Replace with your CSV file path
    # # input_csv = '../data/AF/2430_data.csv'
    # # output_dir = "../data"       # Replace with your desired output directory
    # # split_dataset_by_tag(input_csv4, output_dir)
    
    # df = pd.read_csv(input_csv1, usecols=['tag-local-identifier', 'location-long', 'location-lat', 'timestamp'])

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



    # Plotting Null Values
    path_pattern = "../../data/SM/*.csv"
    
    # Output directory for plots
    output_dir = "../../data/SM"
    
    # Create output directory if it doesn't exist
    # os.makedirs(output_dir, exist_ok=True)
    
    # Get list of all CSV files matching the pattern
    csv_files = glob.glob(path_pattern)
    
    if not csv_files:
        print(f"No CSV files found in {path_pattern}")
    else:
        print(f"Found {len(csv_files)} CSV files to process")
        
        # Process each CSV file
        for csv_file in csv_files:
            print(f"Processing {csv_file}")
            # save_null_locations_perday(csv_file, output_dir)
            read_csv(csv_file, '12')
