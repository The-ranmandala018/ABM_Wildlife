import pandas as pd
import glob
import os
import xlsxwriter


def interpolate_5to1(x):
    op = []
    for i in x:
        for j in range(5):
            op.append(i)
    return op


def write_strings(string_list, labels, path, pClass):
    """
    :param string_list  : processed strings
    :param path         : path to write
    :param labels       : Labels of each string days
    :return             : None. Writes the strings to the given path
    """
    global timeFrame

    try:
        os.makedirs(path, exist_ok=True)
        print("Directory '%s' created successfully" % path)
        print("Writing strings to '%s' " % path)
    except OSError as error:
        print("Writing strings to '%s' " % path)
    print(path+'.xlsx')
    workbook = xlsxwriter.Workbook(path + '\\Strings_' + pClass + '.xlsx')
    worksheet = workbook.add_worksheet()
    r, c, i = 0, 1, 0

    for time, loc in timeFrame.items():
        worksheet.write(r + 1, 0, time)
        r += 1

    for string in string_list:
        worksheet.write(0, c, labels[i])
        i += 1
        r = 1
        for place in string:
            worksheet.write(r, c, place)
            r += 1
        c += 1

    workbook.close()


# ------------------------------------------------ Create Paths --------------------------------------------------------
os.path.abspath(os.curdir)
os.chdir("..")
main_dir_path = os.path.abspath(os.curdir)

dataPath = "X:\\PROJECTS\\AI COVID\\cov-emulator\\app\\src\\data\\Synthetic_test"
resultsPath = ""
infoPath = main_dir_path + '\\Location_Person Info\\Synthetic'

loc_info = pd.read_excel(infoPath + '\\Location_Info.xlsx')['l_class'].values.tolist()
class_info = pd.read_excel(infoPath + '\\PersonClass_Info.xlsx')['p_class'].values.tolist()
# print(loc_info)

all_days = glob.glob(os.path.join(dataPath, "*_person_info.csv"))
# all_days = glob.glob(os.path.join(dataPath, "*[!a-z].csv"))
# print(all_days)

# -------------------------------------------- Extract Strings ---------------------------------------------------------
stored_Strings = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

for dayPath in all_days[:]:
    #print(dayPath)
    day = dayPath.split("\\")[-1].split('_')[0]
    print("Reading day: ", day)
    person_Numbers = pd.read_csv(dayPath)['person'].values.tolist()
    person_Classes = pd.read_csv(dayPath)['person_class'].values.tolist()
    data1 = pd.read_csv(dayPath)['route'].values.tolist()
    data = list(map(lambda x: x.split(' '), data1))
    # ----------------Iterate through Each String for that day ---------------------

    for i in range(len(data)):
        string = data[i]
        data_Label = 'Day' + day + '_' + str(person_Numbers[i]) + '_' + class_info[int(person_Classes[i])]
        #print(data_Label)
        #print(string)
        decoded_String = []
        for loc in string:
            decoded_String.append(loc_info[int(loc)])
        decoded_String = interpolate_5to1(decoded_String)
        stored_Strings[person_Classes[i]][data_Label] = decoded_String

#print(stored_Strings)

# ----------------------------------------------- Time Frame -----------------------------------------------------------
    timeFrame = {}
    H, M = 0, 0
    while H < 24:
        timeFrame[str(H).zfill(2) + ':' + str(M).zfill(2) + ':00'] = '0'
        M += 1
        if M > 59:
            M = 0
            H += 1

# ---------------------------------------- Print Strings to Excel -----------------------------------------------------

n = 0
for occupation in stored_Strings:
    save_path = main_dir_path + '\\Synthetic Results\\Synthetic Location Strings\\' + class_info[n]
    data_labels = list(occupation.keys())
    data_points = list(occupation.values())
    write_strings(data_points, data_labels, save_path, class_info[n])
    print("")
    n+=1
