import pandas as pd
import numpy as np
import os
from numpy import linalg as LA
from sklearn.cluster import KMeans

# ----------------------------------------------- Spectral clustering --------------------------------------------------

def convert_String_to_Numerical_Regular(string_array):
    """
    In order to perform calculations on the String data, we need to convert each location into a numerical value.

    :param string_array : The string array.
    :return             : The numerical coded string array.
    """
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
    n = len(location_list) - 1  # since taking the indexes >>>> len()-1 = 42.
    numeric_array = []
    for location in string_array:
        numeric_array.append(location_list.index(location) / n)

    return numeric_array


def convert_String_to_Numerical_BinaryEncoding(string_array):
    """
    In order to perform calculations on the String data, we need to convert each location into a numerical value.
    :param string_array : Location strings
    :return             : binary zone coded numerical array
    """
    my_dict = {'_home': 0, '_w_home': 1, 'ResidentialZone': 2, 'ResidentialPark': 3, 'RuralBlock': 4, 'Home': 5,
               'AvgProvince': 16, 'COVIDQuarantineZone': 17,
               'DenseDistrict': 18, 'SparseDistrict': 19, 'TestCenter': 20, 'BusStation': 32, 'TukTukStation': 33,
               'AdministrativeZone': 48, 'AdminOffice': 49,
               'AdminWorkArea': 50, '_work': 64, 'CommercialBuilding': 65, 'CommercialCanteen': 66,
               'CommercialFinancialZone': 67, 'CommercialWorkArea': 68,
               'GatheringPlace': 69, 'UrbanBlock': 70, 'FastFoodJoint': 71, 'Restaurants': 72, 'Hospital': 73,
               'MedicalZone': 74, 'Bank': 75, 'ShoppingMall': 76,
               'SuperMarkets': 77, 'RetailShops': 78, 'AgriculturalZone': 80, 'Estate': 81,
               'LivestockCultivateArea': 82, 'PlantCultivateArea': 83, 'Classroom': 96,
               'EducationZone': 97, 'School': 98, 'SchoolCanteen': 99, 'IndustrialManufactureZone': 112,
               'GarmentBuilding': 113, 'GarmentCanteen': 114,
               'GarmentOffice': 115, 'GarmentWorkArea': 116}
    numeric_array = string_array
    for y in range(len(string_array)):
        numeric_array[y] = my_dict[string_array[y]]/116

    return numeric_array


def get_stringData_from_Excel(path, convert_to_numerical=True, encoding='BinaryZones'):
    """
    Extracts excell data from a given path. (For a class)
    :param path                 : Specify the path of the excell folder that you need to extract strings
    :param convert_to_numerical : If to return data points as strings or coded numerical values
    :param encoding             : The method  to encode the strings to numerical values (Regular, BinaryZones)
    :return                     : Data labels and Data points.
    """
    df = pd.read_excel(path)
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    # print(df)
    data_labels = list(df.columns)
    data_points = []

    for label in data_labels:
        if convert_to_numerical:
            if encoding == 'Regular':
                data_points.append(convert_String_to_Numerical_Regular(df[label].values.tolist()))
            elif encoding== 'BinaryZones':
                data_points.append(convert_String_to_Numerical_BinaryEncoding(df[label].values.tolist()))
            # Fill here for other encodings later...

        else:
            data_points.append(df[label].values.tolist())

    if convert_to_numerical:
        # Return as a np array
        return data_labels, np.array(data_points)
    else:
        # return as a string list
        return data_labels, data_points


def get_multipleClass_StringData(classes, convert_to_numerical=True, encoding='BinaryZones'):
    os.path.abspath(os.curdir)
    os.chdir("..")
    main_dir_path = os.path.abspath(os.curdir)
    dir = main_dir_path + '\\Results\\Location Strings'

    path = dir + classes[0] + '\\Strings_' + classes[0][1:] + '.xlsx'

    data_labels, data_points = get_stringData_from_Excel(path, convert_to_numerical=convert_to_numerical, encoding=encoding)

    print('Details of Class: ', classes[0][1:])
    print('Available labels: ', data_labels)
    print(len(data_points))
    for Class in classes[1:]:
        print('')
        print('Details of Class: ', Class[1:])
        path = dir + Class + '\\Strings_' + Class[1:] + '.xlsx'
        Class_data_labels, Class_data_points = get_stringData_from_Excel(path, convert_to_numerical=convert_to_numerical, encoding=encoding)
        print('Available labels: ', Class_data_labels)
        print('Points from class', len(Class_data_points))

        data_labels = data_labels + Class_data_labels
        data_points = np.append(data_points, Class_data_points, axis=0)
    print('')
    print('Total Data Points = ', len(data_points))
    print(data_labels)

    return data_labels, data_points


def spectral_Clustering_Eigen_Decompose(y, x, sigma, selfSimilarity, laplacian='SNL'):
    """
    Performs The eigen decomposition on the spectral Graph
    :param y        : Data labels
    :param x        : Data points
    :param sigma    : Tuning parameter
    :param laplacian: The type of laplacian to use (UL, SNL-Default, RWL)
    :param selfSimilarity : Set relation with itself
    :return         : A list [Eigen Values, Eigen Vectors]
    """
    # ------------------------------------ Generate ADJACENCY MATRIX ---------------------------------------------------
    # Adjacency matrix is a symmetric matrix with shape = (n,n)

    n = len(y)
    W = (-1) * np.ones((n, n))

    # sigma = 0.5
    roundTo = 6

    r, c = 0, 0
    for r in range(n):
        for c in range(n):
            if r == c:
                W[r, c] = selfSimilarity
            elif W[c, r] >= 0:
                W[r, c] = W[c, r]
            else:
                val = (-1) * ((LA.norm(x[r] - x[c]) ** 2) / (2 * (sigma ** 2)))
                W[r, c] = round(np.exp(val), roundTo)

    #print(W)
    # print(LA.norm(data_points[0]-data_points[1]))

    # ------------------------------------ Generate DEGREE MATRIX ------------------------------------------------------
    D = np.zeros((n, n))

    d = []
    r, c = 0, 0
    for r in range(n):
        di = 0
        for c in range(n):
            di += W[r, c]
        d.append(di)

    # print("")
    for i in range(len(d)):
        D[i, i] = d[i]

    # print("")
   # print(D)

    # ------------------------------------ Generate LAPLACIAN MATRIX ---------------------------------------------------
    if laplacian == 'UL':
        L = D - W
    elif laplacian == 'SNL':
        D_ = np.identity(n)
        for i in range(n):
            if D[i, i]==0:
                D_[i, i] = 0
            else:
                D_[i, i] = D[i, i] ** (-0.5)
        L = np.identity(n) - np.matmul(np.matmul(D_ , W), D_)
        #L = LA.inv(D)*W
    elif laplacian == 'RWL':
        L = np.identity(n) - np.matmul(LA.inv(D), W)
    # print("")
    #print(L)

    # ------------------------------------ EIGEN DECOMPOSITION ---------------------------------------------------------

    eigenvalues, eigenvectors = LA.eig(L)

    eigenvalues = np.round(eigenvalues, 3)
    eigenvectors = np.round(eigenvectors, 3)

    return [eigenvalues, eigenvectors]


def perform_kmeans_clustering(data, num_clusters):
    """
    Perform k-means clustering on the given data.

    Parameters:
    - data: The input data for clustering.
    - num_clusters: Number of clusters to form.

    Returns:
    - cluster_labels: Array containing cluster labels assigned to each data point.
    """
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(data)
    return cluster_labels

from datetime import datetime
def isWeekday(Day):
    Day = list(map(int, Day.split('-')))
    day_ = datetime(Day[0], Day[1], Day[2])
    if day_.weekday() < 5:  # 0-mon,1,2,3,4-fri
        return 'Weekday'
    else:  # 5-sat,6-sun
        return 'Weekend'

def print_cluster_assignments(data_labels, cluster_labels):
    """
    Print the cluster assignments for each data point.

    Parameters:
    - data_labels: List of labels corresponding to each data point.
    - cluster_labels: Array containing cluster labels assigned to each data point.
    """
    for i in range(len(data_labels)):
        print(data_labels[i], isWeekday(data_labels[i].split('_')[0]), "=", cluster_labels[i])



'''
def sort_Eigen(eig_Val, eig_Vec):
    eig_Dic = dict(map(lambda i, j: (i, j), eig_Val, eig_Vec))
    eig_Sorted = {k: v for k, v in sorted(eig_Dic.items())}
    eigenvalues_Sorted = list(eig_Sorted.keys())
    eigenvectors_Sorted = list(eig_Sorted.values())
    return [eigenvalues_Sorted, eigenvectors_Sorted]


def compute_MAX_EigenGap_Clusters(eigen_values):
    maxGap = 0
    clusters = 0
    sorted_eigen_values = np.sort(eigen_values)

    for i in range(1, len(sorted_eigen_values) - 1):
        currGap = sorted_eigen_values[i + 1] - sorted_eigen_values[i]
        if currGap > maxGap:
            maxGap = currGap
            clusters = i + 1
    return [maxGap, clusters]
'''