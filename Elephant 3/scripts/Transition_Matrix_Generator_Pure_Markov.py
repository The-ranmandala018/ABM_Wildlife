# import glob
# import os
# import pandas as pd
# import xlsxwriter
# import numpy as np
# from Custom_Modules.StringGeneration import *

# # Set Paths
# os.path.abspath(os.curdir)
# os.chdir("..")
# main_dir_path = os.path.abspath(os.curdir)

# # Define target and parameters
# target = '\\sm'
# work_loc = 'Home'
# entries_per_day = 142

# path_num = os.path.join(main_dir_path, 'clusters', target[1:])  # Numbered CSV file locations
# csv_files_num = glob.glob(os.path.join(path_num, "*.csv"))

# path_catalog = os.path.join(main_dir_path, 'catalogues', target[1:])  # Catalogues location
# csv_files_catalog = glob.glob(os.path.join(path_catalog, "*.xlsx"))

# string_path = os.path.join(main_dir_path, 'Results', 'Location Strings Pure Markov', target[1:])
# prob_matrix_path = os.path.join(main_dir_path, 'Results', 'Probability Matrices Pure Markov', target[1:])
# prob_matrix_csv_path = os.path.join(main_dir_path, 'Results', 'prob_mat_pure_markov_csv', target[1:])

# # Ensure directories exist
# os.makedirs(string_path, exist_ok=True)
# os.makedirs(prob_matrix_path, exist_ok=True)
# os.makedirs(prob_matrix_csv_path, exist_ok=True)

# # Function to check for rest places
# def check_both_and_find_last(dic, elem1, elem2):
#     found_elem1 = False
#     found_elem2 = False
#     last_element = None

#     for value in dic.values():
#         value_str = str(value)
#         if elem1 in value_str:
#             found_elem1 = True
#             last_element = elem1
#         if elem2 in value_str:
#             found_elem2 = True
#             last_element = elem2

#     return found_elem1 and found_elem2, last_element

# # Process CSV and catalog files
# array_of_Dic_Strings = []
# total_usable_days = 0
# usable_days = []

# print(csv_files_catalog)
# for f in csv_files_num:
#     dic_Array = []
#     df = pd.read_csv(f)
#     f_name = os.path.basename(f)
#     numbered_cluster = df["Cluster_DBSCAN_0.0005_10"].values.tolist()

#     for fl in csv_files_catalog:
#         fl_name = os.path.basename(fl)
#         csv_name = f_name.split("_")[0]
#         catalog_name = fl_name.split("_")[0]

#         if csv_name == catalog_name:
#             dic = {}
#             print(f"{csv_name} = {catalog_name} -----> found")
#             df_tag = pd.read_excel(fl, header=None)
#             key = df_tag.iloc[:, [0]].values.tolist()
#             tag = df_tag.iloc[:, [1]].values.tolist()

#             date_ = df['Date'][0]
#             for i in range(len(numbered_cluster)):
#                 timeStamp = df['Time'][i]
#                 if df['Date'][i] != date_:
#                     if len(dic) >= entries_per_day:
#                         dic_Array.append(dic)
#                         usable_days.append(date_ + '_' + csv_name)
#                         total_usable_days += 1
#                     date_ = df['Date'][i]
#                     dic = {}

#                 if numbered_cluster[i] in (-1, "-1"):
#                     dic[timeStamp] = "O_L"
#                 else:
#                     for j in range(len(key)):
#                         if numbered_cluster[i] == key[j][0]:
#                             dic[timeStamp] = "O_L" if tag[j][0] == '-1' else 'Home' if tag[j][0] == '_home' else tag[j][0]

#             array_of_Dic_Strings.extend(dic_Array)

# print(f'Total_usable_days: {total_usable_days}')
# print(f'Length of array_of_Dic_Strings: {len(array_of_Dic_Strings)}')

# # Process strings and set resting place
# processed_Strings = []
# timeFrame = {}
# H, M = 5, 0  # Start at 5:00 AM
# while H < 19:  # End at 7:00 PM
#     timeFrame[f"{H:02d}:{M:02d}:00"] = '0'
#     M += 5
#     if M >= 60:
#         M = 0
#         H += 1
#     if H == 19 and M > 0:
#         break

# for dic in array_of_Dic_Strings:
#     elem1, elem2 = 'Home', '_w_home'
#     both_present, last_element = check_both_and_find_last(dic, elem1, elem2)
#     RestPlace = '_w_home' if both_present or last_element == '_w_home' else 'Home' if last_element == 'Home' else work_loc

#     times = []
#     locations = []

#     for key, value in dic.items():
#         time_parts = key.split(':')
#         hour = int(time_parts[0])
#         minute = int(time_parts[1])
#         if 5 <= hour < 19 or (hour == 19 and minute == 0):
#             times.append(key)
#             locations.append(value)

#     n = 0
#     last = len(times) - 1
#     for key in timeFrame.keys():
#         if n == 0:
#             if compare_Time(key, '<', times[n]):
#                 timeFrame[key] = RestPlace
#             elif compare_Time(key, '>', times[n]):
#                 n += 1
#         if n > last:
#             timeFrame[key] = RestPlace
#         else:
#             if compare_Time(key, '<', times[n]):
#                 timeFrame[key] = locations[n]
#             else:
#                 n += 1
#                 timeFrame[key] = RestPlace if n >= last else locations[n]

#     processed_loc = [value for value in timeFrame.values()]
#     processed_Strings.append(processed_loc)

# # Clean outliers
# def cleaning_outliers(str_matrix, timeFrame, rest_place='Home'):
#     valid_times = list(timeFrame.keys())
#     max_outlier_threshold = 36  # 3 hours = 36 * 5-minute intervals
#     for row in str_matrix:
#         count = 0
#         count_initial = 0
#         current = None
#         previous_value = None
#         for i in range(len(valid_times)):
#             if row[i] in ("O_L", "-1", -1):
#                 row[i] = '-1'
#                 if previous_value is not None:
#                     count += 1
#                 else:
#                     count_initial += 1
#             else:
#                 current = i
#                 current_value = row[current]
#                 if current - count - 1 >= 0:
#                     previous_value = row[current - count - 1]
#                 if count <= max_outlier_threshold or count_initial <= max_outlier_threshold:
#                     if count != 0 and count_initial == 0:
#                         for k in range(current - count, current):
#                             row[k] = previous_value
#                     if count == 0 and count_initial != 0:
#                         for k in range(current - count_initial, current):
#                             row[k] = current_value
#                 count = 0
#                 count_initial = 0

#         for i in range(len(valid_times)):
#             if row[i] == '-1':
#                 if i > 0 and row[i - 1] != '-1':
#                     row[i] = row[i - 1]
#                 else:
#                     row[i] = rest_place

#         if '-1' in row:
#             print(f"Warning: Row still contains '-1' values: {row}")

#     return str_matrix

# processed_Strings = cleaning_outliers(processed_Strings, timeFrame)

# # Write strings to Excel
# def write_strings(string_list, path, target):
#     if not string_list:
#         print(f"Warning: No strings to write for target {target}. Skipping...")
#         return
#     try:
#         os.makedirs(path, exist_ok=True)
#         print(f"Directory '{path}' created successfully")
#         print(f"Writing strings to '{path}'")
#     except OSError as error:
#         print(f"Error creating directory '{path}': {error}")
#         return

#     workbook = xlsxwriter.Workbook(os.path.join(path, f'Pure_Markov_Location_Strings_{target[1:]}.xlsx'))
#     worksheet = workbook.add_worksheet()
#     r, c, i = 0, 1, 0

#     for time in timeFrame.keys():
#         worksheet.write(r + 1, 0, time)
#         r += 1

#     for string in string_list:
#         if i < len(usable_days):
#             worksheet.write(0, c, usable_days[i])
#         else:
#             worksheet.write(0, c, f"Day_{i+1}")
#         i += 1
#         r = 1
#         for place in string:
#             worksheet.write(r, c, place)
#             r += 1
#         c += 1

#     workbook.close()

# # Write Markov transition probability matrix
# def write_probability_matrix_markov(string_list, path, csv_path, target):
#     if not string_list:
#         print(f"Warning: No strings for Markov matrix for target {target}. Skipping...")
#         return
#     location_list = [
#          '_home',
#     '_w_home',
#     '_work',
#     'A',
#     'B',
#     'C',
#     'D',
#     'E',
#     'F',
#     'G',
#     'H',
#     'I',
#     'J',
#     'K',
#     'L',
#     'M',
#     'N',
#     'O',
#     'P',
#     'Q',
#     'R',
#     'S',
#     'T',
#     'U',
#     'V',
#     'W',
#     'X',
#     'Y',
#     'Z',
#     'AA',
#     'AB',
#     'AC',
#     'AD',
#     'AE',
#     'AF',
#     'AG',
#     'AH',
#     'AI',
#     'AJ',
#     'AK',
#     'AL'
#     ]

#     n_locations = len(location_list)
#     transition_counts = [[0] * n_locations for _ in range(n_locations)]
    
#     for sequence in string_list:
#         for i in range(len(sequence) - 1):
#             current_loc = sequence[i]
#             next_loc = sequence[i + 1]
#             if current_loc in location_list and next_loc in location_list:
#                 row_idx = location_list.index(current_loc)
#                 col_idx = location_list.index(next_loc)
#                 transition_counts[row_idx][col_idx] += 1

#     Matrix = [[0.0] * n_locations for _ in range(n_locations)]
#     for i in range(n_locations):
#         total_transitions = sum(transition_counts[i])
#         if total_transitions > 0:
#             for j in range(n_locations):
#                 Matrix[i][j] = transition_counts[i][j] / total_transitions

#     Matrix = np.array(Matrix)
#     print("----------- Markov Transition Probability Matrix --------------------")
#     print(Matrix)
#     s = Matrix.shape

#     try:
#         os.makedirs(path, exist_ok=True)
#         print(f"Directory '{path}' created successfully")
#         print(f"Writing Markov matrix to '{path}'")
#     except OSError as error:
#         print(f"Error creating directory '{path}': {error}")
#         return

#     xls_fname = f"Probability Matrix Markov_allDays_{target[1:]}.xlsx"
#     xls_wb_loc = os.path.join(path, xls_fname)
#     workbook = xlsxwriter.Workbook(xls_wb_loc)
#     worksheet = workbook.add_worksheet()
#     worksheet.write(0, 0, "Current Location")
#     for col_idx, loc in enumerate(location_list, start=1):
#         worksheet.write(0, col_idx, loc)
#         worksheet.write(col_idx, 0, loc)

#     for r in range(1, s[0] + 1):
#         for c in range(1, s[1] + 1):
#             worksheet.write(r, c, Matrix[r - 1, c - 1])

#     workbook.close()

#     # Convert to CSV
#     conv_to_csv(xls_wb_loc, xls_fname, csv_path)

# # Convert Excel to CSV
# def conv_to_csv(xls_loc: str, xls_name: str, csv_dir: str):
#     df = pd.concat(pd.read_excel(xls_loc, sheet_name=None), ignore_index=True)
#     if not df.empty:
#         try:
#             os.makedirs(csv_dir, exist_ok=True)
#             print(f"CSV Directory '{csv_dir}' created successfully")
#             print(f"Writing Matrix to '{csv_dir}'")
#         except OSError as error:
#             print(f"Error creating CSV directory '{csv_dir}': {error}")
#             return

#         csv_loc = os.path.join(csv_dir, xls_name.replace(".xlsx", ".csv"))
#         df.to_csv(csv_loc, index=False)

# # Execute processing
# write_strings(processed_Strings, string_path, target)
# write_probability_matrix_markov(processed_Strings, prob_matrix_path, prob_matrix_csv_path, target)
# print("Processing complete.")



# Transition Matrix Generator - Pure Markov for Baboon Data 3.00 AM to 3.00 PM
# Transition Matrix Generator - Pure Markov for Baboon Data 3.00 AM to 3.00 PM
import glob
import os
import pandas as pd
import xlsxwriter
import numpy as np
from Custom_Modules.StringGeneration import *

# Set Paths
os.path.abspath(os.curdir)
os.chdir("..")
main_dir_path = os.path.abspath(os.curdir)

# Define targets and parameters
targets = ['af', 'am', 'jm', 'sf', 'sm']
default_loc = 'Home'
entries_per_day = 142 # Minimum number of data points (location records) required for a day's data to be considered valid for processing

# Function to check for rest places
def check_for_rest_place(dic, rest_place):
    found_rest = False
    for value in dic.values():
        value_str = str(value)
        if rest_place in value_str:
            found_rest = True
            break
    return found_rest

# Process each target
for target in targets:
    target = '\\' + target  # Add leading backslash for path compatibility
    path_num = os.path.join(main_dir_path, 'clusters', target[1:])  # Numbered CSV file locations
    csv_files_num = glob.glob(os.path.join(path_num, "*.csv"))

    path_catalog = os.path.join(main_dir_path, 'catalogues', target[1:])  # Catalogues location
    csv_files_catalog = glob.glob(os.path.join(path_catalog, "*.xlsx"))

    string_path = os.path.join(main_dir_path, 'Results', 'Location Strings Pure Markov_Baboon', target[1:])
    prob_matrix_path = os.path.join(main_dir_path, 'Results', 'Probability Matrices Pure Markov_Baboon', target[1:])
    prob_matrix_csv_path = os.path.join(main_dir_path, 'Results', 'prob_mat_pure_markov_baboon_csv', target[1:])

    # Ensure directories exist
    os.makedirs(string_path, exist_ok=True)
    os.makedirs(prob_matrix_path, exist_ok=True)
    os.makedirs(prob_matrix_csv_path, exist_ok=True)

    # Process CSV and catalog files
    array_of_Dic_Strings = []
    total_usable_days = 0
    usable_days = []

    print(f"\nProcessing target: {target[1:]}")
    print(csv_files_catalog)
    for f in csv_files_num:
        dic_Array = []
        df = pd.read_csv(f)
        f_name = os.path.basename(f)
        numbered_cluster = df["Cluster_DBSCAN_0.0005_10"].values.tolist()

        for fl in csv_files_catalog:
            fl_name = os.path.basename(fl)
            csv_name = f_name.split("_")[0]
            catalog_name = fl_name.split("_")[0]

            if csv_name == catalog_name:
                dic = {}
                print(f"{csv_name} = {catalog_name} -----> found")
                df_tag = pd.read_excel(fl, header=None)
                key = df_tag.iloc[:, [0]].values.tolist()
                tag = df_tag.iloc[:, [1]].values.tolist()

                date_ = df['Date'][0]
                for i in range(len(numbered_cluster)):
                    timeStamp = df['Time'][i]
                    if df['Date'][i] != date_:
                        if len(dic) >= entries_per_day:
                            dic_Array.append(dic)
                            usable_days.append(date_ + '_' + csv_name)
                            total_usable_days += 1
                        date_ = df['Date'][i]
                        dic = {}

                    if numbered_cluster[i] in (-1, "-1"):
                        dic[timeStamp] = "O_L"
                    else:
                        for j in range(len(key)):
                            if numbered_cluster[i] == key[j][0]:
                                dic[timeStamp] = "O_L" if tag[j][0] == '-1' else tag[j][0]

                array_of_Dic_Strings.extend(dic_Array)

    print(f'Total_usable_days for {target[1:]}: {total_usable_days}')
    print(f'Length of array_of_Dic_Strings for {target[1:]}: {len(array_of_Dic_Strings)}')

    # Process strings and set resting place
    processed_Strings = []
    timeFrame = {}
    H, M = 3, 0  # Start at 3:00 AM
    while H < 15:  # End at 3:00 PM
        timeFrame[f"{H:02d}:{M:02d}:00"] = '0'
        M += 5
        if M >= 60:
            M = 0
            H += 1
        if H == 15 and M > 0:
            break

    location_list = [
        'ForagingGrounds',
        'WaterSources',
        'Home',
        'HumanAreas',
    ]

    for dic in array_of_Dic_Strings:
        rest_place = 'Home'
        found_rest = check_for_rest_place(dic, rest_place)
        RestPlace = rest_place if found_rest else default_loc

        times = []
        locations = []

        for key, value in dic.items():
            time_parts = key.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            if 3 <= hour < 15 or (hour == 15 and minute == 0):
                if value in location_list or value == "O_L":
                    times.append(key)
                    locations.append(value)
                else:
                    times.append(key)
                    locations.append("O_L")  # Replace unrecognized locations with O_L

        n = 0
        last = len(times) - 1
        for key in timeFrame.keys():
            if n == 0:
                if compare_Time(key, '<', times[n]):
                    timeFrame[key] = RestPlace
                elif compare_Time(key, '>', times[n]):
                    n += 1
            if n > last:
                timeFrame[key] = RestPlace
            else:
                if compare_Time(key, '<', times[n]):
                    timeFrame[key] = locations[n]
                else:
                    n += 1
                    timeFrame[key] = RestPlace if n >= last else locations[n]

        processed_loc = [value for value in timeFrame.values()]
        processed_Strings.append(processed_loc)

    # Clean outliers
    def cleaning_outliers(str_matrix, timeFrame, rest_place='Home'):
        valid_times = list(timeFrame.keys())
        max_outlier_threshold = 36  # 3 hours = 36 * 5-minute intervals
        for row in str_matrix:
            count = 0
            count_initial = 0
            current = None
            previous_value = None
            for i in range(len(valid_times)):
                if row[i] in ("O_L", "-1", -1):
                    row[i] = '-1'
                    if previous_value is not None:
                        count += 1
                    else:
                        count_initial += 1
                else:
                    current = i
                    current_value = row[current]
                    if current - count - 1 >= 0:
                        previous_value = row[current - count - 1]
                    if count <= max_outlier_threshold or count_initial <= max_outlier_threshold:
                        if count != 0 and count_initial == 0:
                            for k in range(current - count, current):
                                row[k] = previous_value
                        if count == 0 and count_initial != 0:
                            for k in range(current - count_initial, current):
                                row[k] = current_value
                    count = 0
                    count_initial = 0

            for i in range(len(valid_times)):
                if row[i] == '-1':
                    if i > 0 and row[i - 1] != '-1':
                        row[i] = row[i - 1]
                    else:
                        row[i] = rest_place

            if '-1' in row:
                print(f"Warning: Row still contains '-1' values for {target[1:]}: {row}")

        return str_matrix

    processed_Strings = cleaning_outliers(processed_Strings, timeFrame)

    # Write strings to Excel
    def write_strings(string_list, path, target):
        if not string_list:
            print(f"Warning: No strings to write for target {target}. Skipping...")
            return
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Directory '{path}' created successfully")
            print(f"Writing strings to '{path}'")
        except OSError as error:
            print(f"Error creating directory '{path}': {error}")
            return

        workbook = xlsxwriter.Workbook(os.path.join(path, f'Pure_Markov_Location_Strings_{target[1:]}.xlsx'))
        worksheet = workbook.add_worksheet()
        r, c, i = 0, 1, 0

        for time in timeFrame.keys():
            worksheet.write(r + 1, 0, time)
            r += 1

        for string in string_list:
            if i < len(usable_days):
                worksheet.write(0, c, usable_days[i])
            else:
                worksheet.write(0, c, f"Day_{i+1}")
            i += 1
            r = 1
            for place in string:
                worksheet.write(r, c, place)
                r += 1
            c += 1

        workbook.close()

    # Write Markov transition probability matrix
    def write_probability_matrix_markov(string_list, path, csv_path, target):
        if not string_list:
            print(f"Warning: No strings for Markov matrix for target {target}. Skipping...")
            return
        location_list = [
            'ForagingGrounds',
            'WaterSources',
            'Home',
            'HumanAreas',
        ]

        n_locations = len(location_list)
        transition_counts = [[0] * n_locations for _ in range(n_locations)]
        
        for sequence in string_list:
            for i in range(len(sequence) - 1):
                current_loc = sequence[i]
                next_loc = sequence[i + 1]
                if current_loc in location_list and next_loc in location_list:
                    row_idx = location_list.index(current_loc)
                    col_idx = location_list.index(next_loc)
                    transition_counts[row_idx][col_idx] += 1

        Matrix = [[0.0] * n_locations for _ in range(n_locations)]
        for i in range(n_locations):
            total_transitions = sum(transition_counts[i])
            if total_transitions > 0:
                for j in range(n_locations):
                    Matrix[i][j] = transition_counts[i][j] / total_transitions

        Matrix = np.array(Matrix)
        print(f"----------- Markov Transition Probability Matrix for {target[1:]} --------------------")
        print(Matrix)
        s = Matrix.shape

        try:
            os.makedirs(path, exist_ok=True)
            print(f"Directory '{path}' created successfully")
            print(f"Writing Markov matrix to '{path}'")
        except OSError as error:
            print(f"Error creating directory '{path}': {error}")
            return

        xls_fname = f"Probability Matrix Markov_allDays_{target[1:]}.xlsx"
        xls_wb_loc = os.path.join(path, xls_fname)
        workbook = xlsxwriter.Workbook(xls_wb_loc)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "Current Location")
        for col_idx, loc in enumerate(location_list, start=1):
            worksheet.write(0, col_idx, loc)
            worksheet.write(col_idx, 0, loc)

        for r in range(1, s[0] + 1):
            for c in range(1, s[1] + 1):
                worksheet.write(r, c, Matrix[r - 1, c - 1])

        workbook.close()

        # Convert to CSV
        conv_to_csv(xls_wb_loc, xls_fname, csv_path)

    # Convert Excel to CSV
    def conv_to_csv(xls_loc: str, xls_name: str, csv_dir: str):
        df = pd.concat(pd.read_excel(xls_loc, sheet_name=None), ignore_index=True)
        if not df.empty:
            try:
                os.makedirs(csv_dir, exist_ok=True)
                print(f"CSV Directory '{csv_dir}' created successfully")
                print(f"Writing Matrix to '{csv_dir}'")
            except OSError as error:
                print(f"Error creating CSV directory '{csv_dir}': {error}")
                return

            csv_loc = os.path.join(csv_dir, xls_name.replace(".xlsx", ".csv"))
            df.to_csv(csv_loc, index=False)

    # Execute processing for the current target
    write_strings(processed_Strings, string_path, target)
    write_probability_matrix_markov(processed_Strings, prob_matrix_path, prob_matrix_csv_path, target)

print("Processing complete for all targets.")