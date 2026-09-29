#importing packages

#libraries for data representation
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')

#libraries for data manupilation
import pandas as pd
import numpy as np 
import seaborn as sns  #pip install seaborn

#progress bar for log running codes
from tqdm import tqdm

#clustering libraries
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.datasets import make_blobs
from sklearn.neighbors import KNeighborsClassifier

#requested widget libraries
from ipywidgets import interactive   #necessary for jupiternote book execution
from collections import defaultdict  #necessary for handling datatypes

#imports
# import hdbscan  # conda install -c conda-forge folium if necessary
import folium   #install pip install chardet if it is required
import re
import os       #to access folder paths
import webbrowser

#some color schemes
cols = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
        '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', 
        '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', 
        '#000075', '#808080']*10

#setting plot backgrounds to white
sns.set(style="white")   

#cluster plotter  function

def clusterplotter(df,clustercolumn):
    mapping_2 = folium.Map(location=[df['location-lat'].mean(),df['location-long'].mean()], zoom_start= 9, tiles="OpenStreet Map")
        
    for _, row in df.iterrows():
        if row[clustercolumn] == -1:
            cluster_colour = '#000000'
        else:
            cluster_colour = cols[row[clustercolumn]]
                
        folium.CircleMarker(location=[row['location-lat'], row['location-long']],
                            radius=5,
                            color = cluster_colour,
                            fill = True,
                            fill_color = cluster_colour,
                            ).add_to(mapping_2)
    return mapping_2


in_f = "../data"

# Set DBSCAN properties
epsilon = 0.0005
minPTS  = 10

# config = "eps5minPTS10"
config = f"eps{int(epsilon*10000)}minPTS{minPTS}"
print(config)

for occ in os.listdir(in_f):

    folderpath = f"{in_f}/{occ}"
    allpeople  = os.listdir(folderpath)
    numberofpeople = len(allpeople)

    print(occ)
    df = pd.read_csv(f'{folderpath}/Collective movement in wild baboons-gps-3of4.csv')
    print(df.head())

# for people in range(numberofpeople):
    
#     #reading the xlsx
#     fname = allpeople[people]
#     interest = allpeople[people].replace("@tiec.lk.csv","").replace("@tiec.ok.csv","").replace("@riec.lk.csv","")

    # filepath = f"{folderpath}/{fname}"
    # df       = pd.read_csv(filepath)
    
    # print("\n\n"+interest+"\n")
    # print(df.head())

    #removing the repetitions and NaNs

    #finding out duplicates and NaN values

    # df.duplicated(subset=['Date','Time']).values.any()
    # df.isna().values.any()

    # #removing repetitions and NaN Values

    # print(f'Number of points before Removal_{interest} \t: \t df.shape = {df.shape} ',)        
    # df.dropna(inplace=True)                                                                 #inplace = True to edit the same dataframe ratherthan creating a new one.
    # df.drop_duplicates(subset = ['Date','Time'], keep = 'first', inplace = True)   # remove the duplicates depending on Date and Time both   
    # print(f'Number of points after Removal_{interest} \t: \t df.shape = {df.shape} ',)

    parentpath_map = f"../maps/{occ}"
    folderpath_map = os.path.join(parentpath_map)
    
    if not os.path.exists(folderpath_map):
        os.makedirs(folderpath_map)
    
    #scatter plots

    Data = np.array(df[['location-lat','location-long']],dtype='float64')
    plt.scatter(Data[:,0],Data[:,1],alpha=0.2,s=50)
    plt.savefig(f"{folderpath_map}/_scatterplot.png")

    #map object generation

    mapping = folium.Map(location=[df['location-lat'].mean(), df['location-long'].mean()], zoom_start=9, tiles='OpenStreetMap')

    for _, row in df.iterrows():
        folium.CircleMarker(location=[row['location-lat'], row['location-long']],
        radius=5,
        #popup=re.sub(r'[^a-zA-Z ]+', '', row.NAME),
        color='#1787FE',
        fill=True,
        fill_colour='#1787FE').add_to(mapping)

    #saving as a map

    mapping.save(f"{folderpath_map}/_Map.html")

    #Clustering-Kmeans

    #kmeans clustering
    X = np.array(df[['location-lat','location-long']],dtype='float64')
    clusters = 3   
    Model_kmeans = KMeans(n_clusters=clusters, random_state=17).fit(X)      #random state ensures the reproducibility of the data
    Model_Predictions = Model_kmeans.predict(X)                             #extracting the predictors
    df[f'Cluster_Kmeans{clusters}'] = Model_Predictions                     #adding the predictior to the dataframe

    map = clusterplotter(df,f'Cluster_Kmeans{clusters}')
    map.save(f"{folderpath_map}/_Map_Kmeans.html")

    #DBSCAN

    Model_DBSCAN = DBSCAN(eps=epsilon,min_samples=minPTS).fit(X)
    Model_Predictions_DBSCAN = Model_DBSCAN.labels_
    df[f'Cluster_DBSCAN_{epsilon}_{minPTS}']  = Model_Predictions_DBSCAN
    map_DBSCAN = clusterplotter(df,f'Cluster_DBSCAN_{epsilon}_{minPTS}')
    map_DBSCAN.save(f"{folderpath_map}/_Map_DBSCAN_{config}.html")
    
    #saving 
    csvparentpath = f"../clusters/{occ}"
    csvfolderpath = csvparentpath
    # csvfolderpath = os.path.join(csvparentpath,interest)
    
    if not os.path.exists(csvfolderpath):
        os.makedirs(csvfolderpath)
    
    df.to_csv(f"{csvfolderpath}/_{config}_ClusterData.csv")
