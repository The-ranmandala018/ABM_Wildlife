import pandas as pd
from Custom_Modules.SpectralClustering import *
import os


# Number of clusters
sigma = 5.8
n_clusters = 4
split_vec = n_clusters
self_similarity = 1

targets = ['\\st']

writer = True


enc = 'BinaryZones'
# enc = 'Regular'

#lap = 'UL'
lap = 'SNL'
# lap = 'RWL'


data_labels, data_points = get_multipleClass_StringData(classes=targets, encoding=enc)

[eigVal, eigVec] = spectral_Clustering_Eigen_Decompose(data_labels, data_points, sigma, selfSimilarity=self_similarity, laplacian=lap)
print(eigVal)


#eigVec = eigVec[:,0:split_vec]

eigVec = eigVec[:,0:n_clusters]

filtered_eigVec = np.real(eigVec)

# Perform k-means clustering
cluster_labels = perform_kmeans_clustering(filtered_eigVec, n_clusters)


# Print cluster assignments
print_cluster_assignments(data_labels, cluster_labels)
print(cluster_labels)

# =============================== Write Separate clusters to Excel =====================================================
print("")
os.path.abspath(os.curdir)
#os.chdir("..")
main_dir_path = os.path.abspath(os.curdir)
if writer==True:
    res_path = main_dir_path+ '\\Results\Clustered Location Strings'+ targets[0]
    string_path = main_dir_path + '\\Results\\Location Strings' + targets[0]+ '\Strings_' + targets[0][1:]+'.xlsx'

    f = open(res_path+'\\info_'+targets[0][1:]+'.txt', 'w')
    f.write('Sigma = {}, Self Similarity(SS) = {}\n\n'.format(sigma,self_similarity))
    try:
        os.makedirs(res_path, exist_ok=True)
        print("Directory '%s' created successfully" % res_path)
        print("Writing strings to '%s' " % res_path)
    except OSError as error:
        print("Writing strings to '%s' " % res_path)

    strings = pd.read_excel(string_path)
    Output = []
    # print(strings)
    for c in range(n_clusters):
        Output.append(pd.DataFrame())
        Output[c]['Time'] = strings['Time']

    for i in range(len(data_labels)):
        Output[cluster_labels[i]][data_labels[i]] = strings[data_labels[i]]

    for cluster in range(n_clusters):
        print('Writing to: ', res_path+str(cluster)+'.xlsx')
        f.write('Strings_'+targets[0][1:]+'_cluster'+str(cluster)+'.xlsx :\n')
        Output[cluster].to_excel(res_path+ '\Strings_' + targets[0][1:]+'_cluster'+str(cluster)+'.xlsx' , index=False)

    f.close()
