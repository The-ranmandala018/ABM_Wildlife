import glob
import os
import pandas as pd
import xlsxwriter
from Custom_Modules.StringGeneration import *


os.path.abspath(os.curdir)
os.chdir("..")
main_dir_path = os.path.abspath(os.curdir)
# ------------------------------ Set Paths --------------------------------------------------------
target = '\\gw'

path_num = main_dir_path + '\\numbered' + target  # Numbered CSV file locations
csv_files_num = glob.glob(os.path.join(path_num, "*.csv"))

path_catalog = main_dir_path+ '\\catalogues' + target  # Catalogues location
csv_files_catalog = glob.glob(os.path.join(path_catalog, "*.xlsx"))

string_path = main_dir_path + '\\Results\Location Strings' + target
allDays_prob_matrix_path = main_dir_path + '\\Results\Probability Matrices' + target
allDays_stayDuration_matrix_path = main_dir_path + '\\Results\Stay Duration Matrices' + target
weekDays_prob_matrix_path = main_dir_path + '\\Results\Probability Matrices' + target
weekEnds_stayDuration_matrix_path = main_dir_path + '\\Results\Stay Duration Matrices' + target

# ---------------------------------- Get the string array -----------------------------------------------------

array_of_Dic_Strings_allDays = []
array_of_Dic_Strings_weekDays = []
array_of_Dic_Strings_weekEnds = []


total_usable_days = 0
usable_days = []
# LOOP OVER THE LIST OF CSV FILES

# print(path_num)
# print(path_catalog)

print(csv_files_catalog)
print(csv_files_num)

for f in csv_files_num:
    #print(f)       # all catalogs are not yet generated
    dic_Array = []
    # read the csv file
    df = pd.read_csv(f)

    f_name=f.split("\\")[-1]

    # CLUSTER NUMBER COLUMN NAME
    numbered_cluster = df["Cluster_DBSCAN_0.0005_10"].values.tolist()
    for fl in csv_files_catalog:
        #print(fl)
        fl_name=fl.split("\\")[-1]                  #CATALOG FILE NAME SPLIT
        epsminPTS=fl_name.split("_")[-1]            #EPSMINPTS VALUE

        csv_name=f_name.split("_")[0]
        catalog_name = fl_name.split("_")[0]

        if(csv_name==catalog_name):
            numbered_cluster_copy=[]
            dic_val=[]
            data_dict=[]
            dic = {}
            print(csv_name,"=",catalog_name,"-----> found")
            # df_tag = pd.read_csv(fl, header=None)

            df_tag = pd.read_excel(fl, header=None)

            key=df_tag.iloc[:, [0]].values.tolist()
            tag= df_tag.iloc[:, [1]].values.tolist()

            date_ = df['Date'][0]
            for i in range(len(numbered_cluster)):
                timeStamp = df['Time'][i]

                if df['Date'][i]!=date_:
                    if len(dic)>=250:
                        dic_Array.append(dic)
                        usable_days.append(date_ + ' ' + csv_name)
                        total_usable_days += 1
                        #print(len(dic))
                    date_=df['Date'][i]
                    # CLEARING THE LISTS
                    dic = {}

                if numbered_cluster[i]== -1:    #Replacing cluster number -1 (Outliers) with O_L
                    numbered_cluster_copy.append("O_L")
                    dic[timeStamp] = "O_L"
                else:                           #If not an outlier; replacing with the relavent tags
                    for j in range(len(key)):
                        if numbered_cluster[i]==key[j][0]:
                            numbered_cluster_copy.append(tag[j][0])
                            dic[timeStamp] = tag[j][0]

    array_of_Dic_Strings_allDays = array_of_Dic_Strings_allDays + dic_Array

print('Total_usable_days: ',total_usable_days)

# ---------------------------------------------------------- Cleaning of String Array ----------------------------------

processed_Strings = []
for dic in array_of_Dic_Strings:
    # Set the Resting Place
    if 'home' in dic.values():
        RestPlace = 'home'
    elif '_home' in dic.values():
        RestPlace = '_home'
    elif 'Home' in dic.values():
        RestPlace = 'Home'
    else:
        RestPlace = 'home'

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

    # ----------------------------------------- Write Strings to excel -----------------------------------------------------


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

    workbook = xlsxwriter.Workbook(path+'\Strings_'+target[1:]+'.xlsx')
    worksheet = workbook.add_worksheet()
    r, c, i = 0, 1, 0

    for time, loc in timeFrame.items():
        worksheet.write(r+1, 0, time)
        r+=1

    for string in string_list:
        worksheet.write(0,c, usable_days[i])
        i+=1
        r = 1
        for place in string:
            worksheet.write(r, c, place)
            r+=1
        c+=1

    workbook.close()


def write_probability_matrix(string_list, path):
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
        'AdministrativeZone',
        'AdminOffice',
        'AdminWorkArea',
        'AgriculturalZone',
        'AvgProvince',
        'Bank',
        'BusStation',
        'Classroom',
        'CommercialBuilding',
        'CommercialCanteen',
        'CommercialFinancialZone',
        'CommercialWorkArea',
        'COVIDQuarantineZone',
        'DenseDistrict',
        'EducationZone',
        'Estate',
        'FastFoodJoint',
        'GarmentBuilding',
        'GarmentCanteen',
        'GarmentOffice',
        'GarmentWorkArea',
        'GatheringPlace',
        'Home',
        'Hospital',
        'IndustrialManufactureZone',
        'LivestockCultivateArea',
        'MedicalZone',
        'PlantCultivateArea',
        'ResidentialPark',
        'ResidentialZone',
        'Restaurants',
        'RetailShops',
        'RuralBlock',
        'School',
        'SchoolCanteen',
        'ShoppingMall',
        'SparseDistrict',
        'SuperMarkets',
        'TestCenter',
        'TukTukStation',
        'UrbanBlock'
    ]
    Matrix = probability_matrix(string_list, location_list)
    print(Matrix)
    s = Matrix.shape

    try:
        os.makedirs(path, exist_ok=True)
        print("Directory '%s' created successfully" % path)
        print("Writing Matrix to '%s' " % path)
    except OSError as error:
        print("Writing Matrix to '%s' " % path)

    workbook = xlsxwriter.Workbook(path+"\Probability Matrix_allDays_"+target[1:]+".xlsx")
    worksheet = workbook.add_worksheet()

    r, c = 0, 0
    #print(s)
    #print('len of places: ', len(location_list))
    for r in range(s[0]):
        for c in range(s[1]):
            worksheet.write(r, c, Matrix[r, c])

    workbook.close()


write_strings(processed_Strings, string_path)
write_probability_matrix(processed_Strings, prob_matrix_path)