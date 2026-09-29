import numpy as np
import pandas as pd
from datetime import datetime


def check_Probability(i, j, loc, string_List_x):
    """
    :param      i: i th position (across)
    :param      j: j th position (down)
    :param      loc: Location Array
    :param      string_List_x: String lists of locations [S1,S2,S3,......,Sn)
    :return:    The probability of being at the particular place at the given time
    """
    count = 0.0
    for n in range(len(string_List_x)):
        if string_List_x[n][i] == loc[j]:
            count = count + 1
    return float(count) / float(len(string_List_x))


s1 = list('HHWSH')
s2 = list('HWWSH')
s3 = list('HWWWH')

locations = ['H', 'W', 'S']


def probability_matrix(x, locations):
    """
    :param x         : list of String lists
    :param locations : Location list
    :return          : The probability Matrix
    """
    a = np.zeros(shape=(len(locations), len(x[0])))
    for i in range((len(x[0]))):
        for j in range(len(locations)):
            a[j][i] = check_Probability(i, j, locations, x)
    return a


print(probability_matrix([s1, s2, s3], locations))


def compare_Time(str1, cmp, str2):
    """
    :param str1 : time 1
    :param cmp  : > or <
    :param str2 : time 2
    :return: True or False
    """
    DTM1 = str1.split(':')
    DTM2 = str2.split(':')
    status = None
    if int(DTM1[0]) > int(DTM2[0]):
        status = True
    elif int(DTM1[0]) < int(DTM2[0]):
        status = False
    else:
        if int(DTM1[1]) > int(DTM2[1]):
            status = True
        elif int(DTM1[1]) < int(DTM2[1]):
            status = False
        else:
            if int(DTM1[2]) > int(DTM2[2]):
                status = True
            elif int(DTM1[2]) < int(DTM2[2]):
                status = False
            else:
                return False  # Returns this if equal

    if cmp == '>':
        return status
    else:
        return not status


def isWeekday(Day):
    Day = list(map(int, Day.split('-')))
    day_ = datetime(Day[0], Day[1], Day[2])
    if day_.weekday() < 5:  # 0-mon,1,2,3,4-fri
        return 'Weekday'
    else:  # 5-sat,6-sun
        return 'Weekend'

# print(compare_Time('08:01:23', '>', '8:1:23'))

# ----------------------------------------- STAY DURATION MATRIX -------------------------------------------------------

def count_same_eliments(string_day, location_list, mat_2d):
    for x in range(len(location_list)):
        # for x in range(1):
        count = 0
        flag = 0

        for y in range(len(string_day)):
            if (location_list[x] == string_day[y]):
                count = count + 1
                flag = 1

            if ((location_list[x] != string_day[y]) and (flag == 1)):
                flag = 0
                mat_2d[x][count - 1] = mat_2d[x][count - 1] + 1
                count = 0

            if (flag == 1 and y == (len(string_day) - 1)):
                flag = 0
                mat_2d[x][count - 1] = mat_2d[x][count - 1] + 1
                count = 0

    return mat_2d
def count_same_eliments_2DMatrix(string_day_2d,location_list):
    cols=len(string_day_2d[0])
    rows= len(location_list)
    matrix=(rows, cols)
    arr = np.zeros(matrix , dtype=float)

    for g in range(len(string_day_2d)):
        count_same_eliments(string_day_2d[g],location_list,arr)
    return arr


def stayDuration_matrix(stringList, locations):
    mat = count_same_eliments_2DMatrix(stringList, locations)
    s = mat.sum(axis=1)
    print('S',s)
    #print(mat)
    #print(mat.shape)

    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            if s[r] == 0:
                mat[r, c] = 0
            else:
                mat[r, c] = mat[r, c] / s[r]

    return mat

