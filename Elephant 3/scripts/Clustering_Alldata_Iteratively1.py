# #importing packages

# #libraries for data representation
# import matplotlib
# import matplotlib.pyplot as plt
# plt.style.use('ggplot')

# #libraries for data manupilation
# import pandas as pd
# import numpy as np 
# import seaborn as sns  #pip install seaborn

# #progress bar for log running codes
# from tqdm import tqdm

# #clustering libraries
# from sklearn.cluster import KMeans, DBSCAN
# from sklearn.metrics import silhouette_score
# from sklearn.datasets import make_blobs
# from sklearn.neighbors import KNeighborsClassifier

# #requested widget libraries
# from ipywidgets import interactive   #necessary for jupiternote book execution
# from collections import defaultdict  #necessary for handling datatypes

# #imports
# # import hdbscan  # conda install -c conda-forge folium if necessary
# import folium   #install pip install chardet if it is required
# import re
# import os       #to access folder paths
# import webbrowser

# #some color schemes
# cols = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
#         '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', 
#         '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', 
#         '#000075', '#808080']*100

# #setting plot backgrounds to white
# sns.set(style="white")   

# #cluster plotter  function

# def clusterplotter(df,clustercolumn):
#     mapping_2 = folium.Map(location=[df.Latitude.mean(),df.Longitude.mean()], zoom_start= 9, tiles="OpenStreetMap")
        
#     for _, row in df.iterrows():
#         if row[clustercolumn] == -1:
#             cluster_colour = '#000000'
#         else:
#             cluster_colour = cols[row[clustercolumn]]
                
#         folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
#                             radius=5,
#                             color = cluster_colour,
#                             fill = True,
#                             fill_color = cluster_colour,
#                             ).add_to(mapping_2)
#     return mapping_2


# in_f = "../data"

# # Set DBSCAN properties
# epsilon = 0.001
# minPTS  = 15

# # config = "eps5minPTS10"
# config = f"eps{int(epsilon*10000)}minPTS{minPTS}"
# print(config)

# for occ in os.listdir(in_f):

#     folderpath = f"{in_f}/{occ}"
#     allpeople  = os.listdir(folderpath)
#     numberofpeople = len(allpeople)

#     for people in range(numberofpeople):
        
#         #reading the xlsx
#         fname = allpeople[people]
#         interest = allpeople[people].replace(".csv","")

#         filepath = f"{folderpath}/{fname}"
#         df       = pd.read_csv(filepath)
        
#         print("\n\n"+interest+"\n")
#         print(df.head())

#         #removing the repetitions and NaNs
        
#         #finding out duplicates and NaN values

#         # df.duplicated(subset=['Date','Time']).values.any()
#         df.isna().values.any()

#         #removing repetitions and NaN Values
        
#         print(f'Number of points before Removal_{interest} \t: \t df.shape = {df.shape} ',)        
#         df.dropna(inplace=True)                                                                 #inplace = True to edit the same dataframe ratherthan creating a new one.
#         # df.drop_duplicates(subset = ['Date','Time'], keep = 'first', inplace = True)   # remove the duplicates depending on Date and Time both   
#         print(f'Number of points after Removal_{interest} \t: \t df.shape = {df.shape} ',)

#         parentpath_map = f"../maps/{occ}"
#         folderpath_map = os.path.join(parentpath_map,interest)
        
#         if not os.path.exists(folderpath_map):
#             os.makedirs(folderpath_map)
        
#         #scatter plots

#         Data = np.array(df[['Latitude','Longitude']],dtype='float64')
#         plt.scatter(Data[:,0],Data[:,1],alpha=0.2,s=50)
#         plt.savefig(f"{folderpath_map}/{interest}_scatterplot.png")

#         #map object generation

#         mapping = folium.Map(location=[df.Latitude.mean(), df.Longitude.mean()], zoom_start=9, tiles='OpenStreetMap')

#         for _, row in df.iterrows():
#             folium.CircleMarker(location=[row.Latitude, row.Longitude],
#             radius=5,
#             #popup=re.sub(r'[^a-zA-Z ]+', '', row.NAME),
#             color='#1787FE',
#             fill=True,
#             fill_colour='#1787FE').add_to(mapping)

#         #saving as a map

#         mapping.save(f"{folderpath_map}/{interest}_Map.html")

#         #Clustering-Kmeans

#         #kmeans clustering
#         X = np.array(df[['Latitude','Longitude']],dtype='float64')
#         clusters = 3   
#         Model_kmeans = KMeans(n_clusters=clusters, random_state=17).fit(X)      #random state ensures the reproducibility of the data
#         Model_Predictions = Model_kmeans.predict(X)                             #extracting the predictors
#         df[f'Cluster_Kmeans{clusters}'] = Model_Predictions                     #adding the predictior to the dataframe

#         map = clusterplotter(df,f'Cluster_Kmeans{clusters}')
#         map.save(f"{folderpath_map}/{interest}_Map_Kmeans.html")

#         #DBSCAN

#         Model_DBSCAN = DBSCAN(eps=epsilon,min_samples=minPTS).fit(X)
#         Model_Predictions_DBSCAN = Model_DBSCAN.labels_
#         df[f'Cluster_DBSCAN_{epsilon}_{minPTS}']  = Model_Predictions_DBSCAN
#         map_DBSCAN = clusterplotter(df,f'Cluster_DBSCAN_{epsilon}_{minPTS}')
#         map_DBSCAN.save(f"{folderpath_map}/{interest}_Map_DBSCAN_{config}.html")
        
#         #saving 
#         csvparentpath = f"../clusters/{occ}"
#         csvfolderpath = csvparentpath
#         # csvfolderpath = os.path.join(csvparentpath,interest)
        
#         if not os.path.exists(csvfolderpath):
#             os.makedirs(csvfolderpath)
        
#         df.to_csv(f"{csvfolderpath}/{interest}_{config}_ClusterData.csv")


# -------------- -------------------Colors For Different Dates----------------------------------------
# import matplotlib
# import matplotlib.pyplot as plt
# plt.style.use('ggplot')

# #libraries for data manupilation
# import pandas as pd
# import numpy as np 
# import seaborn as sns  #pip install seaborn

# #progress bar for log running codes
# from tqdm import tqdm

# #clustering libraries
# from sklearn.cluster import KMeans, DBSCAN
# from sklearn.metrics import silhouette_score
# from sklearn.datasets import make_blobs
# from sklearn.neighbors import KNeighborsClassifier

# #requested widget libraries
# from ipywidgets import interactive   #necessary for jupiternote book execution
# from collections import defaultdict  #necessary for handling datatypes

# #imports
# # import hdbscan  # conda install -c conda-forge folium if necessary
# import folium   #install pip install chardet if it is required
# import re
# import os       #to access folder paths
# import webbrowser

# #some color schemes
# cols = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
#         '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', 
#         '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', 
#         '#000075', '#808080']*100

# #setting plot backgrounds to white
# sns.set(style="white")   

# #cluster plotter  function

# def clusterplotter(df,clustercolumn):
#     mapping_2 = folium.Map(location=[df.Latitude.mean(),df.Longitude.mean()], zoom_start= 9, tiles="OpenStreetMap")
        
#     for _, row in df.iterrows():
#         if row[clustercolumn] == -1:
#             cluster_colour = '#000000'
#         else:
#             cluster_colour = cols[row[clustercolumn]]
                
#         folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
#                             radius=5,
#                             color = cluster_colour,
#                             fill = True,
#                             fill_color = cluster_colour,
#                             ).add_to(mapping_2)
#     return mapping_2


# in_f = "../data"

# # Set DBSCAN properties
# epsilon = 0.001
# minPTS  = 15

# # config = "eps5minPTS10"
# config = f"eps{int(epsilon*10000)}minPTS{minPTS}"
# print(config)

# for occ in os.listdir(in_f):

#     folderpath = f"{in_f}/{occ}"
#     allpeople  = os.listdir(folderpath)
#     numberofpeople = len(allpeople)

#     for people in range(numberofpeople):
        
#         #reading the xlsx
#         fname = allpeople[people]
#         interest = allpeople[people].replace(".csv","")

#         filepath = f"{folderpath}/{fname}"
#         df       = pd.read_csv(filepath)
        
#         print("\n\n"+interest+"\n")
#         print(df.head())

#         #removing the repetitions and NaNs
        
#         #finding out duplicates and NaN values

#         # df.duplicated(subset=['Date','Time']).values.any()
#         df.isna().values.any()

#         #removing repetitions and NaN Values
        
#         print(f'Number of points before Removal_{interest} \t: \t df.shape = {df.shape} ',)        
#         df.dropna(inplace=True)                                                                 #inplace = True to edit the same dataframe ratherthan creating a new one.
#         # df.drop_duplicates(subset = ['Date','Time'], keep = 'first', inplace = True)   # remove the duplicates depending on Date and Time both   
#         print(f'Number of points after Removal_{interest} \t: \t df.shape = {df.shape} ',)

#         parentpath_map = f"../maps/{occ}"
#         folderpath_map = os.path.join(parentpath_map,interest)
        
#         if not os.path.exists(folderpath_map):
#             os.makedirs(folderpath_map)
        
#         #scatter plots

#         Data = np.array(df[['Latitude','Longitude']],dtype='float64')
#         plt.scatter(Data[:,0],Data[:,1],alpha=0.2,s=50)
#         plt.savefig(f"{folderpath_map}/{interest}_scatterplot.png")

#         #map object generation

#         mapping = folium.Map(location=[df.Latitude.mean(), df.Longitude.mean()], zoom_start=9, tiles='OpenStreetMap')
        
#         # Assign colors to unique dates
#         unique_dates = df['Date'].unique()
#         date_colors = {date: cols[i % len(cols)] for i, date in enumerate(unique_dates)}
        
#         for _, row in df.iterrows():
#             date_color = date_colors[row['Date']]
#             folium.CircleMarker(location=[row.Latitude, row.Longitude],
#             radius=5,
#             #popup=re.sub(r'[^a-zA-Z ]+', '', row.NAME),
#             color=date_color,
#             fill=True,
#             fill_color=date_color,
#             popup=f"DateTime: {row['DateTime']}").add_to(mapping)

        

#         #saving as a map

#         mapping.save(f"{folderpath_map}/{interest}_Map.html")

#         #Clustering-Kmeans

#         #kmeans clustering
#         X = np.array(df[['Latitude','Longitude']],dtype='float64')
#         clusters = 3   
#         Model_kmeans = KMeans(n_clusters=clusters, random_state=17).fit(X)      #random state ensures the reproducibility of the data
#         Model_Predictions = Model_kmeans.predict(X)                             #extracting the predictors
#         df[f'Cluster_Kmeans{clusters}'] = Model_Predictions                     #adding the predictior to the dataframe

#         map = clusterplotter(df,f'Cluster_Kmeans{clusters}')
#         map.save(f"{folderpath_map}/{interest}_Map_Kmeans.html")

#         #DBSCAN

#         Model_DBSCAN = DBSCAN(eps=epsilon,min_samples=minPTS).fit(X)
#         Model_Predictions_DBSCAN = Model_DBSCAN.labels_
#         df[f'Cluster_DBSCAN_{epsilon}_{minPTS}']  = Model_Predictions_DBSCAN
#         map_DBSCAN = clusterplotter(df,f'Cluster_DBSCAN_{epsilon}_{minPTS}')
#         map_DBSCAN.save(f"{folderpath_map}/{interest}_Map_DBSCAN_{config}.html")
        
#         #saving 
#         csvparentpath = f"../clusters/{occ}"
#         csvfolderpath = csvparentpath
#         # csvfolderpath = os.path.join(csvparentpath,interest)
        
#         if not os.path.exists(csvfolderpath):
#             os.makedirs(csvfolderpath)
        
#         df.to_csv(f"{csvfolderpath}/{interest}_{config}_ClusterData.csv")

 
# ------------------------------ Differenct Colours for Different Months ------------------------------

# import matplotlib
# import matplotlib.pyplot as plt
# plt.style.use('ggplot')

# #libraries for data manupilation
# import pandas as pd
# import numpy as np 
# import seaborn as sns  #pip install seaborn

# #progress bar for log running codes
# from tqdm import tqdm

# #clustering libraries
# from sklearn.cluster import KMeans, DBSCAN
# from sklearn.metrics import silhouette_score
# from sklearn.datasets import make_blobs
# from sklearn.neighbors import KNeighborsClassifier

# #requested widget libraries
# from ipywidgets import interactive   #necessary for jupiternote book execution
# from collections import defaultdict  #necessary for handling datatypes

# #imports
# # import hdbscan  # conda install -c conda-forge folium if necessary
# import folium   #install pip install chardet if it is required
# import re
# import os       #to access folder paths
# import webbrowser

# #some color schemes
# cols = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
#         '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', 
#         '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', 
#         '#000075', '#808080']*100

# #setting plot backgrounds to white
# sns.set(style="white")   

# #cluster plotter  function

# def clusterplotter(df,clustercolumn):
#     mapping_2 = folium.Map(location=[df.Latitude.mean(),df.Longitude.mean()], zoom_start= 9, tiles="OpenStreetMap")
        
#     for _, row in df.iterrows():
#         if row[clustercolumn] == -1:
#             cluster_colour = '#000000'
#         else:
#             cluster_colour = cols[row[clustercolumn]]
                
#         folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
#                             radius=5,
#                             color = cluster_colour,
#                             fill = True,
#                             fill_color = cluster_colour,
#                             ).add_to(mapping_2)
#     return mapping_2


# in_f = "../data"

# # Set DBSCAN properties
# epsilon = 0.001
# minPTS  = 15

# # config = "eps5minPTS10"
# config = f"eps{int(epsilon*10000)}minPTS{minPTS}"
# print(config)

# for occ in os.listdir(in_f):

#     folderpath = f"{in_f}/{occ}"
#     allpeople  = os.listdir(folderpath)
#     numberofpeople = len(allpeople)

#     for people in range(numberofpeople):
        
#         #reading the xlsx
#         fname = allpeople[people]
#         interest = allpeople[people].replace(".csv","")

#         filepath = f"{folderpath}/{fname}"
#         df       = pd.read_csv(filepath)
        
#         print("\n\n"+interest+"\n")
#         print(df.head())

#         #removing the repetitions and NaNs
        
#         #finding out duplicates and NaN values

#         # df.duplicated(subset=['Date','Time']).values.any()
#         df.isna().values.any()

#         #removing repetitions and NaN Values
        
#         print(f'Number of points before Removal_{interest} \t: \t df.shape = {df.shape} ',)        
#         df.dropna(inplace=True)                                                                 #inplace = True to edit the same dataframe ratherthan creating a new one.
#         # df.drop_duplicates(subset = ['Date','Time'], keep = 'first', inplace = True)   # remove the duplicates depending on Date and Time both   
#         print(f'Number of points after Removal_{interest} \t: \t df.shape = {df.shape} ',)

#         # Create DateTime column
#         df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

#         parentpath_map = f"../maps/{occ}"
#         folderpath_map = os.path.join(parentpath_map,interest)
        
#         if not os.path.exists(folderpath_map):
#             os.makedirs(folderpath_map)
        
#         #scatter plots

#         Data = np.array(df[['Latitude','Longitude']],dtype='float64')
#         plt.scatter(Data[:,0],Data[:,1],alpha=0.2,s=50)
#         plt.savefig(f"{folderpath_map}/{interest}_scatterplot.png")

#         #map object generation

#         mapping = folium.Map(location=[df.Latitude.mean(), df.Longitude.mean()], zoom_start=9, tiles='OpenStreetMap')
        
#         # Assign colors to unique months
#         unique_months = sorted(df['DateTime'].dt.month.unique())
#         month_colors = {month: cols[i % len(cols)] for i, month in enumerate(unique_months)}
        
#         for _, row in df.iterrows():
#             month_color = month_colors[row['DateTime'].month]
#             folium.CircleMarker(location=[row.Latitude, row.Longitude],
#             radius=5,
#             #popup=re.sub(r'[^a-zA-Z ]+', '', row.NAME),
#             color=month_color,
#             fill=True,
#             fill_color=month_color,
#             popup=f"DateTime: {row['DateTime']}, Month: {row['DateTime'].month}").add_to(mapping)

        

#         #saving as a map

#         mapping.save(f"{folderpath_map}/{interest}_Map.html")

#         #Clustering-Kmeans

#         #kmeans clustering
#         X = np.array(df[['Latitude','Longitude']],dtype='float64')
#         clusters = 3   
#         Model_kmeans = KMeans(n_clusters=clusters, random_state=17).fit(X)      #random state ensures the reproducibility of the data
#         Model_Predictions = Model_kmeans.predict(X)                             #extracting the predictors
#         df[f'Cluster_Kmeans{clusters}'] = Model_Predictions                     #adding the predictior to the dataframe

#         map = clusterplotter(df,f'Cluster_Kmeans{clusters}')
#         map.save(f"{folderpath_map}/{interest}_Map_Kmeans.html")

#         #DBSCAN

#         Model_DBSCAN = DBSCAN(eps=epsilon,min_samples=minPTS).fit(X)
#         Model_Predictions_DBSCAN = Model_DBSCAN.labels_
#         df[f'Cluster_DBSCAN_{epsilon}_{minPTS}']  = Model_Predictions_DBSCAN
#         map_DBSCAN = clusterplotter(df,f'Cluster_DBSCAN_{epsilon}_{minPTS}')
#         map_DBSCAN.save(f"{folderpath_map}/{interest}_Map_DBSCAN_{config}.html")
        
#         #saving 
#         csvparentpath = f"../clusters/{occ}"
#         csvfolderpath = csvparentpath
#         # csvfolderpath = os.path.join(csvparentpath,interest)
        
#         if not os.path.exists(csvfolderpath):
#             os.makedirs(csvfolderpath)
        
#         df.to_csv(f"{csvfolderpath}/{interest}_{config}_ClusterData.csv")

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
        '#000075', '#808080']*100

#setting plot backgrounds to white
sns.set(style="white")   

#cluster plotter  function

def clusterplotter(df,clustercolumn):
    mapping_2 = folium.Map(location=[df.Latitude.mean(),df.Longitude.mean()], zoom_start= 9, tiles="OpenStreetMap")
        
    for _, row in df.iterrows():
        if row[clustercolumn] == -1:
            cluster_colour = '#000000'
        else:
            cluster_colour = cols[row[clustercolumn]]
                
        folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
                            radius=5,
                            color = cluster_colour,
                            fill = True,
                            fill_color = cluster_colour,
                            ).add_to(mapping_2)
    return mapping_2


in_f = "../data"

# Set DBSCAN properties
epsilon = 0.001
minPTS  = 15

# config = "eps5minPTS10"
config = f"eps{int(epsilon*10000)}minPTS{minPTS}"
print(config)

for occ in os.listdir(in_f):

    folderpath = f"{in_f}/{occ}"
    allpeople  = os.listdir(folderpath)
    numberofpeople = len(allpeople)

    for people in range(numberofpeople):
        
        #reading the xlsx
        fname = allpeople[people]
        interest = allpeople[people].replace(".csv","")

        filepath = f"{folderpath}/{fname}"
        df       = pd.read_csv(filepath)
        
        print("\n\n"+interest+"\n")
        print(df.head())

        #removing the repetitions and NaNs
        
        #finding out duplicates and NaN values

        # df.duplicated(subset=['Date','Time']).values.any()
        df.isna().values.any()

        #removing repetitions and NaN Values
        
        print(f'Number of points before Removal_{interest} \t: \t df.shape = {df.shape} ',)        
        df.dropna(inplace=True)                                                                 #inplace = True to edit the same dataframe ratherthan creating a new one.
        # df.drop_duplicates(subset = ['Date','Time'], keep = 'first', inplace = True)   # remove the duplicates depending on Date and Time both   
        print(f'Number of points after Removal_{interest} \t: \t df.shape = {df.shape} ',)

        # Create DateTime column
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

        parentpath_map = f"../maps/{occ}"
        folderpath_map = os.path.join(parentpath_map,interest)
        
        if not os.path.exists(folderpath_map):
            os.makedirs(folderpath_map)
        
        #scatter plots

        Data = np.array(df[['Latitude','Longitude']],dtype='float64')
        plt.scatter(Data[:,0],Data[:,1],alpha=0.2,s=50)
        plt.savefig(f"{folderpath_map}/{interest}_scatterplot.png")
        plt.close()

        #map object generation

        mapping = folium.Map(location=[df.Latitude.mean(), df.Longitude.mean()], zoom_start=9, tiles='OpenStreetMap')
        
        # Assign specific colors to months
        month_colors = {
            1: '#008000',   # January: Green
            2: '#FF0000',   # February: Red
            3: '#0000FF',   # March: Blue
            4: '#800080',   # April: Purple
            5: '#FFA500',   # May: Orange
            6: '#00FFFF',   # June: Cyan
            7: '#FFFF00',   # July: Yellow
            8: '#FF00FF',   # August: Magenta
            9: '#A52A2A',   # September: Brown
            10: '#808080',  # October: Gray
            11: '#000080',  # November: Navy
            12: '#FFC0CB'   # December: Pink
        }
        
        for _, row in df.iterrows():
            month_color = month_colors.get(row['DateTime'].month, '#000000')  # Default to black if month not found
            folium.CircleMarker(location=[row.Latitude, row.Longitude],
            radius=5,
            #popup=re.sub(r'[^a-zA-Z ]+', '', row.NAME),
            color=month_color,
            fill=True,
            fill_color=month_color,
            popup=f"DateTime: {row['DateTime']}, Month: {row['DateTime'].month}").add_to(mapping)

        

        #saving as a map

        mapping.save(f"{folderpath_map}/{interest}_Map.html")

        #Clustering-Kmeans

        #kmeans clustering
        X = np.array(df[['Latitude','Longitude']],dtype='float64')
        clusters = 3   
        Model_kmeans = KMeans(n_clusters=clusters, random_state=17).fit(X)      #random state ensures the reproducibility of the data
        Model_Predictions = Model_kmeans.predict(X)                             #extracting the predictors
        df[f'Cluster_Kmeans{clusters}'] = Model_Predictions                     #adding the predictior to the dataframe

        map = clusterplotter(df,f'Cluster_Kmeans{clusters}')
        map.save(f"{folderpath_map}/{interest}_Map_Kmeans.html")

        #DBSCAN

        Model_DBSCAN = DBSCAN(eps=epsilon,min_samples=minPTS).fit(X)
        Model_Predictions_DBSCAN = Model_DBSCAN.labels_
        df[f'Cluster_DBSCAN_{epsilon}_{minPTS}']  = Model_Predictions_DBSCAN
        map_DBSCAN = clusterplotter(df,f'Cluster_DBSCAN_{epsilon}_{minPTS}')
        map_DBSCAN.save(f"{folderpath_map}/{interest}_Map_DBSCAN_{config}.html")
        
        #saving 
        csvparentpath = f"../clusters/{occ}"
        csvfolderpath = csvparentpath
        # csvfolderpath = os.path.join(csvparentpath,interest)
        
        if not os.path.exists(csvfolderpath):
            os.makedirs(csvfolderpath)
        
        df.to_csv(f"{csvfolderpath}/{interest}_{config}_ClusterData.csv")




# --------- Year Wise Clustering and Mapping (with Seasonality) -----------------
#libraries for data representation
# import matplotlib
# import matplotlib.pyplot as plt
# plt.style.use('ggplot')

# #libraries for data manupilation
# import pandas as pd
# import numpy as np 
# import seaborn as sns  #pip install seaborn

# #progress bar for log running codes
# from tqdm import tqdm

# #clustering libraries
# from sklearn.cluster import KMeans, DBSCAN
# from sklearn.metrics import silhouette_score
# from sklearn.datasets import make_blobs
# from sklearn.neighbors import KNeighborsClassifier

# #requested widget libraries
# from ipywidgets import interactive   #necessary for jupiternote book execution
# from collections import defaultdict  #necessary for handling datatypes

# #imports
# # import hdbscan  # conda install -c conda-forge folium if necessary
# import folium   #install pip install chardet if it is required
# import re
# import os       #to access folder paths
# import webbrowser

# #some color schemes
# cols = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
#         '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', 
#         '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', 
#         '#000075', '#808080']*100

# #setting plot backgrounds to white
# sns.set(style="white")   

# #cluster plotter  function

# def clusterplotter(df,clustercolumn):
#     mapping_2 = folium.Map(location=[df.Latitude.mean(),df.Longitude.mean()], zoom_start= 9, tiles="OpenStreetMap")
        
#     for _, row in df.iterrows():
#         if row[clustercolumn] == -1:
#             cluster_colour = '#000000'
#         else:
#             cluster_colour = cols[row[clustercolumn]]
                
#         folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
#                             radius=5,
#                             color = cluster_colour,
#                             fill = True,
#                             fill_color = cluster_colour,
#                             ).add_to(mapping_2)
#     return mapping_2


# in_f = "../data"

# # Set DBSCAN properties
# epsilon = 0.001
# minPTS  = 15

# # config = "eps5minPTS10"
# config = f"eps{int(epsilon*10000)}minPTS{minPTS}"
# print(config)

# for occ in os.listdir(in_f):

#     folderpath = f"{in_f}/{occ}"
#     allfiles  = [f for f in os.listdir(folderpath) if f.endswith('.csv')]
#     numberoffiles = len(allfiles)

#     # Dictionary to group data by (individual, year)
#     groups = defaultdict(list)
    
#     for file_idx in range(numberoffiles):
        
#         fname = allfiles[file_idx]
#         interest = fname.replace(".csv","")

#         filepath = f"{folderpath}/{fname}"
#         df       = pd.read_csv(filepath)
        
#         print("\n\n"+interest+"\n")
#         print(df.head())

#         #removing the repetitions and NaNs
        
#         #finding out duplicates and NaN values
#         df.isna().values.any()

#         #removing repetitions and NaN Values
        
#         print(f'Number of points before Removal_{interest} \t: \t df.shape = {df.shape} ',)        
#         df.dropna(inplace=True)                                                                 #inplace = True to edit the same dataframe ratherthan creating a new one.
#         # df.drop_duplicates(subset = ['Date','Time'], keep = 'first', inplace = True)   # remove the duplicates depending on Date and Time both   
#         print(f'Number of points after Removal_{interest} \t: \t df.shape = {df.shape} ',)

#         # Create DateTime column
#         df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

#         # Parse filename to extract individual, season, year
#         pattern = r'(\d+)(fe|me)_(.*)_(\d{4})\.csv'
#         match = re.match(pattern, fname)
#         if match:
#             num = match.group(1)
#             type_ = match.group(2)
#             season = match.group(3)
#             year = match.group(4)
#             individual = f"{num}{type_}"
#             groups[(individual, year)].append(df)
#         else:
#             print(f"Filename pattern not matched for {fname}, skipping.")

#     # Now process each group (individual, year)
#     for (individual, year), dfs_list in groups.items():
        
#         # Concatenate all seasons for this individual-year
#         df_combined = pd.concat(dfs_list, ignore_index=True)
#         df_combined.sort_values('DateTime', inplace=True)
#         df_combined.reset_index(drop=True, inplace=True)
        
#         print(f"\nCombined data for {individual} {year}: {df_combined.shape[0]} points")
        
#         parentpath_map = f"../maps Seasons( 1 Year)/{occ}"
#         folderpath_map = os.path.join(parentpath_map, f"{individual}_{year}")
        
#         if not os.path.exists(folderpath_map):
#             os.makedirs(folderpath_map)
        
#         #scatter plots
#         Data = np.array(df_combined[['Latitude','Longitude']],dtype='float64')
#         plt.figure()
#         plt.scatter(Data[:,0],Data[:,1],alpha=0.2,s=50)
#         plt.savefig(f"{folderpath_map}/{individual}_{year}_scatterplot.png")
#         plt.close()

#         #map object generation
#         mapping = folium.Map(location=[df_combined.Latitude.mean(), df_combined.Longitude.mean()], zoom_start=9, tiles='OpenStreetMap')
        
#         # Assign specific colors to seasons
#         season_colors = {
#             'Cold-Dry': '#4595e6',
#             'Hot-Wet': '#2E8B57',
#             'Hot-Dry': '#E07B39'
#         }
        
#         for _, row in df_combined.iterrows():
#             season_color = season_colors.get(row['Season'], '#000000')  # Default to black if season not found
#             folium.CircleMarker(location=[row.Latitude, row.Longitude],
#             radius=5,
#             color=season_color,
#             fill=True,
#             fill_color=season_color,
#             popup=f"DateTime: {row['DateTime']}, Season: {row['Season']}").add_to(mapping)

#         #saving as a map
#         mapping.save(f"{folderpath_map}/{individual}_{year}_Map.html")

#         #Clustering-Kmeans
#         #kmeans clustering
#         X = np.array(df_combined[['Latitude','Longitude']],dtype='float64')
#         clusters = 3   
#         Model_kmeans = KMeans(n_clusters=clusters, random_state=17).fit(X)      #random state ensures the reproducibility of the data
#         Model_Predictions = Model_kmeans.predict(X)                             #extracting the predictors
#         df_combined[f'Cluster_Kmeans{clusters}'] = Model_Predictions                     #adding the predictior to the dataframe

#         map_kmeans = clusterplotter(df_combined,f'Cluster_Kmeans{clusters}')
#         map_kmeans.save(f"{folderpath_map}/{individual}_{year}_Map_Kmeans.html")

#         #DBSCAN
#         Model_DBSCAN = DBSCAN(eps=epsilon,min_samples=minPTS).fit(X)
#         Model_Predictions_DBSCAN = Model_DBSCAN.labels_
#         df_combined[f'Cluster_DBSCAN_{epsilon}_{minPTS}']  = Model_Predictions_DBSCAN
#         map_DBSCAN = clusterplotter(df_combined,f'Cluster_DBSCAN_{epsilon}_{minPTS}')
#         map_DBSCAN.save(f"{folderpath_map}/{individual}_{year}_Map_DBSCAN_{config}.html")
        
#         #saving 
#         csvparentpath = f"../clusters Seasons( 1 Year)/{occ}"
#         csvfolderpath = csvparentpath
        
#         if not os.path.exists(csvfolderpath):
#             os.makedirs(csvfolderpath)
        
#         df_combined.to_csv(f"{csvfolderpath}/{individual}_{year}_{config}_ClusterData.csv")

# print("Processing complete.")