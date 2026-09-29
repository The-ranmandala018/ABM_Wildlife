import numpy as np
a = ['1 2','56 34']

b = list(map(lambda x:x.split(' '), a))



a = [{},{},{}]

a[0]['tag'] = 25
a[0]['tog'] = 253

a[2]['tig'] = 333

dic = {'ab':11, 'cd':39}


# ----------------------------------------------------------------------------------------------------------------------


input = [["hi", "hi", "ok", "ok","ok", "hi", "hi", "hi", "hi", "bye", "bye", "hi"],
         ["hi", "ok", "ok", "ok","ok", "hi", "hi", "hi", "hi", "bye", "bye", "hi"],
         ["hi", "hi", "ok", "ok","ok", "hi", "hi", "hi", "hi", "bye", "bye", "hi"],
         ["hi", "hi", "ok", "ok","ok", "hi", "hi", "hi", "hi", "bye", "bye", "hi"],
         ["hi", "hi", "hi", "hi","hi", "hi", "hi", "hi", "hi", "hi", "hi", "hi"]]


b = ["hi", "ok", "bye"]


def interpolate_5to1(x):
    op = []
    for i in x:
        for j in range(5):
            op.append(i)
    return op


a = np.array([[1,2,3,4],
              [0,0,1,2,],
              [1,1,5,1]], dtype=float)

#print(a)
s = a.sum(axis=1)


for r in range(a.shape[0]):
    for c in range(a.shape[1]):

        a[r,c] = a[r,c]/s[r]




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


def get_stayProbability_Matrix(stringList, locations):
    mat = count_same_eliments_2DMatrix(stringList, locations)
    s = mat.sum(axis=1)
    print('S',s)
    print(mat)
    print(mat.shape)

    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            mat[r, c] = mat[r, c] / s[r]

    return mat


print(get_stayProbability_Matrix(input,b))