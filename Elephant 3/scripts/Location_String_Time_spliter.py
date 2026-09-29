import glob
import os
import pandas as pd
import xlsxwriter
from Custom_Modules.StringGeneration import *
import sys
# -------------------------------------------------------------------------------------------------------------
os.path.abspath(os.curdir)
os.chdir("..")
main_dir_path = os.path.abspath(os.curdir)
print('main')
print(main_dir_path)

# ------------------------------ Set Paths --------------------------------------------------------
os.chdir("..")
ABM_path = os.path.abspath(os.curdir)
print(ABM_path)

five_baboon_results_path = ABM_path + '\\5 Baboons\\Results'
print(five_baboon_results_path)





target = '\\af'
#Set work location according to catalogue standard naming
work_loc='School'

path_num = main_dir_path + '\\clusters' + target  # Numbered CSV file locations
print(path_num)
csv_files_num = glob.glob(os.path.join(path_num, "*.csv"))
print(f'csv files num \n{csv_files_num}')

path_catalog = main_dir_path + '\\catalogues' + target  # Catalogues location
csv_files_catalog = glob.glob(os.path.join(path_catalog, "*.xlsx")) #xlsx formet

string_path = main_dir_path + '\\Results\\Location Strings' + target
prob_matrix_path = main_dir_path + '\\Results\\Probability Matrices' + target
stayDuration_matrix_path = main_dir_path + '\\Results\\Stay Duration Matrices' + target
prob_matrix_csv_path = main_dir_path + "\\Results\\prob_mat_csv" + target
stayDuration_matrix_csv_path = main_dir_path + "\\Results\\std_mat_csv" + target

minutes_string_path = main_dir_path + '\\Results\\Divided Location Strings' + target


# # read by default 1st sheet of an excel file
# string_path_excel = string_path + "\\Strings_st.xlsx"
# dataframe1 = pd.read_excel(string_path_excel)

# print(dataframe1)


def divide_exel_data_to_given_min():
    '''
    
    '''
import pandas as pd
import os
import math

# Function to split the Excel file by rows
def split_excel_file_by_rows(input_excel_path, minutes_per_file, output_folder, target_name):
    '''
    input_excel_path    : the excel file path
    minutes_per_file    : minutes that need to break the file
    output_folder       : file path of the new excel 
    target_name         : target class name
    
    '''
    # print('H')
    start_time = 0
    end_time = start_time + minutes_per_file -1
    rows_per_file = minutes_per_file

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # print('H')
    # Read the Excel file
    df = pd.read_excel(input_excel_path)
    
    # Ensure the 'Time' column is present
    if 'Time' not in df.columns:
        raise ValueError("The input file must contain a 'Time' column.")
    
    # Get the total number of data rows (excluding header)
    total_rows = len(df)
    # print(total_rows)
    # Validate the number of rows per file
    if rows_per_file < 1:
        raise ValueError("Number of rows per file must be at least 1.")
    if rows_per_file > total_rows:
        raise ValueError(f"Number of rows per file ({rows_per_file}) cannot be greater than the total number of rows ({total_rows}).")
    # print('H')
    # Calculate the number of files needed
    num_files = math.ceil(total_rows / rows_per_file)
    # print(num_files)

    
    # Split the rows and save each chunk
    for i in range(num_files):
        # Determine the start and end row indices for this chunk
        start_idx = i * rows_per_file
        end_idx = min(start_idx + rows_per_file, total_rows)
        
        # Select the current chunk of rows
        chunk_df = df.iloc[start_idx:end_idx]
    
        # Define the output file path
        output_file = os.path.join(output_folder, f'Strings_{target_name}_{start_time}_{end_time}.xlsx')
        
        # Save the chunk to a new Excel file
        chunk_df.to_excel(output_file, index=False)
        print(f"Saved {output_file} with rows {start_idx} to {end_idx-1} ({len(chunk_df)} rows).")

        start_time = start_time + minutes_per_file
        end_time = end_time + minutes_per_file


# Main execution
if __name__ == "__main__":

    # output_folder = five_baboon_results_path +'\\time split Location Strings'

    min_per_file = 240
    target_name = target.lstrip('\\')

    baboon_results_location_path = five_baboon_results_path + '\\Location Strings'
    # print(baboon_results_location_path)
    # print(output_folder)
    print(target_name )
    # sys.exit()

    for subdir, dirs, files in os.walk(baboon_results_location_path):
        for file in files:
            sub_name = os.path.basename(subdir)
            # print(f'sub dit = {sub_name}')
            # Check if the file is an Excel file (you can add more extensions if needed)
            if file.endswith(('.xlsx', '.xls')):
                # Build the full path to the Excel file
                file_path = os.path.join(subdir, file)
                output_folder = os.path.dirname(os.path.dirname(subdir))+'\\time split Location Strings'+'\\'+sub_name
                # print(output_folder)
                print(f"Found Excel file: {file_path}")
                split_excel_file_by_rows(file_path, min_per_file, output_folder,sub_name)
                print('\n')

                

        
        
    # input_excel_path = string_path + '\\Strings_st.xlsx'
    # output_folder = minutes_string_path

    # min_per_file = 240
    # target_name = target.lstrip('\\')
    # print(type(min_per_file))
    # split_excel_file_by_rows(input_excel_path, min_per_file, output_folder,target_name)
    
    # # Prompt user for the number of rows per file
    # try:
    #     rows_per_file = int(input("Enter the number of rows per split file: "))
    #     split_excel_file_by_rows(input_excel_path, rows_per_file, output_folder,target)
    # except ValueError as e:
    #     print(f"Error: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")

