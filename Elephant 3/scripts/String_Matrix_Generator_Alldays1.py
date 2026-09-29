import glob
import os
import pandas as pd
import xlsxwriter
from Custom_Modules.StringGeneration import *

# -------------------------------------------------------------------------------------------------------------

os.path.abspath(os.curdir)
os.chdir("..")
main_dir_path = os.path.abspath(os.curdir)
# ------------------------------ Set Paths --------------------------------------------------------
target = '\\sm'
#Set work location according to catalogue standard naming
work_loc='Home'
entries_per_day = 142

path_num = main_dir_path + '\\clusters' + target  # Numbered CSV file locations
csv_files_num = glob.glob(os.path.join(path_num, "*.csv"))

path_catalog = main_dir_path + '\\catalogues' + target  # Catalogues location
csv_files_catalog = glob.glob(os.path.join(path_catalog, "*.xlsx")) #xlsx formet

string_path = main_dir_path + '\\Results\\Location Strings' + target
prob_matrix_path = main_dir_path + '\\Results\\Probability Matrices' + target
stayDuration_matrix_path = main_dir_path + '\\Results\\Stay Duration Matrices' + target
prob_matrix_csv_path = main_dir_path + "\\Results\\prob_mat_csv" + target
stayDuration_matrix_csv_path = main_dir_path + "\\Results\\std_mat_csv" + target

#--------Extract restplaces in a day trajectory-----------------------------------#
def check_both_and_find_last(dic, elem1, elem2):
    found_elem1 = False
    found_elem2 = False
    last_element = None

    for value in dic.values():
        value_str = str(value)  # Convert the value to string
        if elem1 in value_str:
            found_elem1 = True
            last_element = elem1
        if elem2 in value_str:
            found_elem2 = True
            last_element = elem2

    return found_elem1 and found_elem2, last_element

# target_elements = [ 'Home', '_w_home'] # Elements we are searching in dictionary (RestPlaces)

# ---------------------------------- Get the string array -----------------------------------------------------

array_of_Dic_Strings = []
total_usable_days = 0
usable_days = []
processed_Strings = []

# LOOP OVER THE LIST OF CSV FILES

print(csv_files_catalog)

for f in csv_files_num:
    # print(f)       # all catalogs are not yet generated
    dic_Array = []
    # read the csv file
    df = pd.read_csv(f)

    f_name = f.split("\\")[-1]

    # CLUSTER NUMBER COLUMN NAME 
    numbered_cluster = df["Cluster_DBSCAN_0.0005_10"].values.tolist()
    for fl in csv_files_catalog:
        print(fl)
        fl_name = fl.split("\\")[-1]  # CATALOG FILE NAME SPLIT
        epsminPTS = fl_name.split("_")[-1]  # EPSMINPTS VALUE

        csv_name = f_name.split("_")[0]
        catalog_name = fl_name.split("_")[0]

        if (csv_name == catalog_name):
            dic = {}
            print(csv_name, "=", catalog_name, "-----> found")
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

                if numbered_cluster[i] == -1 or numbered_cluster[i] == "-1":  # Replacing cluster number -1 (Outliers) with O_L
                    dic[timeStamp] = "O_L"
                else:  # If not an outlier; replacing with the relavent tags
                    for j in range(len(key)):
                        if numbered_cluster[i] == key[j][0]:
                            if tag[j][0] == '-1':
                                dic[timeStamp] = "O_L"
                            elif tag[j][0] == '_home':  #Replacing '_home' with 'Home'
                                dic[timeStamp]= 'Home'
                            else:
                                dic[timeStamp] = tag[j][0]

            array_of_Dic_Strings = array_of_Dic_Strings + dic_Array

print('Total_usable_days: ', total_usable_days)
print(len(array_of_Dic_Strings))

# -------------------------------------------- Setting the Resting Place -----------------------------------------------

processed_Strings = []
RestPlace_prev=''
print(array_of_Dic_Strings)
for dic in array_of_Dic_Strings:
    # Set the Resting Place
    # RestPlace = 'Home'
    # print(dic)

    
    elem1 = 'Home'
    elem2 = '_w_home'
    both_present, last_element = check_both_and_find_last(dic, elem1, elem2)

    if both_present == True:
        RestPlace = '_w_home'
    else:
        if last_element == '_w_home':
            RestPlace = '_w_home'
        elif last_element == 'Home':
            RestPlace = 'Home'
        elif last_element == '_home':
            RestPlace = 'Error'
        else:
            RestPlace = work_loc

    times = []
    locations = []

    # ================================ Time axis ===========================================================================
    timeFrame = {}
    H, M = 0, 0
    while H < 24:
        timeFrame[str(H).zfill(2) + ':' + str(M).zfill(2) + ':00'] = '0'
        M += 1
        if M > 59:
            M = 0
            H += 1

    # print(timeFrame)

    # ======================================================================================================================
    for key, value in dic.items():
        times.append(key)
        locations.append(value)

    # print(locations)

    n = 0
    first, last = 0, len(times) - 1
    # print('last :', last)
    for key, value in timeFrame.items():
        if n == 0:
            if compare_Time(key, '<', times[n]):
                timeFrame[key] = RestPlace
            elif compare_Time(key, '>', times[n]):
                n += 1
        if n > last:
            timeFrame[key] = RestPlace
        else:
            if compare_Time(key, '<', times[n]):
                # print(n)
                timeFrame[key] = locations[n]
            else:
                n += 1
                # print(n, key)
                if (n >= last):
                    timeFrame[key] = RestPlace
                else:
                    timeFrame[key] = locations[n]

    processed_loc = []
    for key, value in timeFrame.items():
        processed_loc.append(value)
    processed_Strings.append(processed_loc)
print(len(processed_Strings))

# ----------------------------------------- Write Strings to excel -----------------------------------------------------

def cleaning_outliers(str_matrix):
    # Replacing "-1" values
    # 1)"-1" s should not be the start of the day
    # 2)Continuous occurance >= 2
    # 3) Then, it will be replaced with the previous String tag

    for row in str_matrix:
        count = 0  # For counting number of consequetive -1
        count_initial = 0
        current = None  # Initiate current value to None
        previous_value = None  # Initialize to None before the first element in each row

        for i in range(len(row)):
            if row[i] == "O_L" or row[i] == "-1" or row[i] == -1:  # Counting number of -1
                row[i] = '-1'
                if previous_value is not None:
                    count += 1
                else:
                    count_initial += 1
            else:
                current = i
                current_value = row[current]
                previous_value = row[current - count - 1]
                if (count <= 180 or count_initial <= 180):
                    if (count != 0 and count_initial == 0):
                        for k in range((current - count), (current)):  # Replace -1 with the previous value
                            row[k] = previous_value
                    if (count == 0 and count_initial != 0):
                        for k in range((current - count_initial), (current)):  # Replace -1 with the previous value
                            row[k] = current_value
                count = 0  # set back to 0
                count_initial = 0  # set back to 0
    return str_matrix


processed_Strings = cleaning_outliers(processed_Strings)


def write_strings(string_list, path):
    """
    :param string_list  : processed strings
    :param path         : path to write
    :return             : None. Writes the strings to the given path
    """
    global timeFrame
    global target
    try:
        os.makedirs(path, exist_ok=True)
        print("Directory '%s' created successfully" % path)
        print("Writing strings to '%s' " % path)
    except OSError as error:
        print("Writing strings to '%s' " % path)

    workbook = xlsxwriter.Workbook(path + '\\Strings_' + target[1:] + '.xlsx')
    # print('path is  ', path+'\Strings_'+target[1:]+'.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, 'Time')
    r, c, i = 0, 1, 0

    for time, loc in timeFrame.items():
        worksheet.write(r + 1, 0, time)
        r += 1

    for string in string_list:
        worksheet.write(0, c, usable_days[i])
        i += 1
        r = 1
        for place in string:
            worksheet.write(r, c, place)
            r += 1
        c += 1

    workbook.close()

write_strings(processed_Strings[:], string_path)


# ----------------------------Probability Matrix -----------------------------------------------------------------------
def write_probability_matrix(string_list, path, csv_path):
    """
    :param string_list  : Processed strings
    :param path         : Path to write
    :return             : None. Writes probability matrix to the given path
    """
    global target
    location_list = [
    '_home',
    '_w_home',
    '_work',
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z',
    'AA',
    'AB',
    'AC',
    'AD',
    'AE',
    'AF',
    'AG',
    'AH',
    'AI',
    'AJ',
    'AK',
    'AL'
]

    Matrix = probability_matrix(string_list, location_list)
    print("----------- Probability Matrix--------------------")
    print(Matrix)
    s = Matrix.shape

    try:
        os.makedirs(path, exist_ok=True)
        print("Directory '%s' created successfully" % path)
        print("Writing Matrix to '%s' " % path)
    except OSError as error:
        print("Writing Matrix to '%s' " % path)

    xls_fname = "Probability Matrix_allDays_" + target[1:] + ".xlsx"
    xls_wb_loc = path + "\\" + xls_fname

    workbook = xlsxwriter.Workbook(xls_wb_loc)
    worksheet = workbook.add_worksheet()
    worksheet.write(0,0,"Locations")
    for timePoint in range(1, 1441):
        colPos = timePoint
        worksheet.write(0, colPos,timePoint)
    r_loc = 1
    for loc in location_list:
        worksheet.write(r_loc, 0, loc)
        r_loc+=1

    for r in range(1,s[0]+1):
        for c in range(1,s[1]+1):
            worksheet.write(r, c, Matrix[r-1, c-1])

    workbook.close()

    conv_to_csv(xls_wb_loc, xls_fname, csv_path)

    # 


# ------------------------ Stay Duration Matrix ------------------------------------------------------------------------

def write_stayduration_matrix(string_list, path, csv_path):
    """
    :param string_list  : Processed strings
    :param path         : Path to write
    :return             : None. Writes probability matrix to the given path
    """
    global target
    location_list = [
    '_home',
    '_w_home',
    '_work',
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z',
    'AA',
    'AB',
    'AC',
    'AD',
    'AE',
    'AF',
    'AG',
    'AH',
    'AI',
    'AJ',
    'AK',
    'AL'
]

    Matrix = stayDuration_matrix(string_list, location_list)
    print("----------- Stay Duration Matrix--------------------")
    print(Matrix)
    s = Matrix.shape

    try:
        os.makedirs(path, exist_ok=True)
        print("Directory '%s' created successfully" % path)
        print("Writing Matrix to '%s' " % path)
    except OSError as error:
        print("Writing Matrix to '%s' " % path)

    xls_fname = "StayDuration Matrix_allDays_" + target[1:] + ".xlsx"
    xls_wb_loc = path + "\\" + xls_fname

    workbook = xlsxwriter.Workbook(xls_wb_loc)
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, "Locations")
    for timePoint in range(1, 1441):
        colPos = timePoint
        worksheet.write(0, colPos,timePoint)

    r_loc = 1
    for loc in location_list:
        worksheet.write(r_loc, 0, loc)
        r_loc += 1

    for r in range(1, s[0] + 1):
        for c in range(1, s[1] + 1):
            worksheet.write(r, c, Matrix[r - 1, c - 1])

    workbook.close()

    conv_to_csv(xls_wb_loc, xls_fname, csv_path)

    #

# ------------------------ Convert Matrices to csv ------------------------------------------------------------------------
def conv_to_csv(xls_loc: str, xls_name: str, csv_dir: str):

    df = pd.concat(pd.read_excel(xls_loc, sheet_name=None), ignore_index=True)

    if(df.empty != 1):

        try:
            os.makedirs(csv_dir, exist_ok=True)
            print("CSV Directory '%s' created successfully" % csv_dir)
            print("Writing Matrix to '%s' " % csv_dir)
        except OSError as error:
            print("Writing Matrix to '%s' " % csv_dir)


        csv_loc = csv_dir + "\\" + xls_name.replace(".xlsx",".csv")

        df.to_csv(csv_loc, index=False)


# write_strings(processed_Strings, string_path)
write_probability_matrix(processed_Strings[:], prob_matrix_path, prob_matrix_csv_path)
# write_strings(processed_Strings, string_path)
write_stayduration_matrix(processed_Strings[:], stayDuration_matrix_path, stayDuration_matrix_csv_path)
