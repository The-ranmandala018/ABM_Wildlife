# # # --------Script to plot clusters with numbered centers and circles around them-----------

import folium
import pandas as pd
import numpy as np
import glob
import os


def clusterplotter(df, cluster_column, cols):
    mapping = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=9, tiles="OpenStreetMap")
    unique_clusters = df[cluster_column].unique()

    for cluster in unique_clusters:
        if cluster == -1:
            cluster_color = ''
        else:
            cluster_color = cols[cluster]

        cluster_df = df[df[cluster_column] == cluster]

        cluster_lat = cluster_df['Latitude'].mean()
        cluster_lon = cluster_df['Longitude'].mean()

        # Calculate the distance between cluster center and farthest point
        cluster_points = cluster_df[['Latitude', 'Longitude']].values
        center = np.array([cluster_lat, cluster_lon]) # save the cluster long lat to csv and with cluster number
        distances = np.linalg.norm(cluster_points - center, axis=1)
        max_distance = np.max(distances)

        folium.Circle(location=[cluster_lat, cluster_lon],
                      radius=max_distance * 160000,  # Convert to meters for radius (if you want this multiply by 1000)
                      color=cluster_color,
                      fill=False,
                      fill_color=cluster_color,
                      ).add_to(mapping)

        # Plot individual GPS points within the cluster
        for _, row in cluster_df.iterrows():
            folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
                                radius=5,
                                color=cluster_color,
                                fill=False,
                                fill_color=cluster_color,
                                ).add_to(mapping)

    return mapping


cols = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
        '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff',
        '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
        '#000075', '#808080'] * 100

occ_path = "../clusters"

numbrd_f = "../numbered"

for occ in os.listdir(occ_path):

    folder_path = f"{occ_path}/{occ}"  # Path to the folder containing the cluster data CSV files

    # Iterate over each file in the folder
    for file_name in os.listdir(folder_path):

        if file_name.endswith(".csv"):  # Process only CSV files

            print(file_name)

            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path)

            # Get the cluster column name
            cluster_column = [column for column in df.columns if column.startswith("Cluster_DBSCAN")][0]

            # Generate the map with clusters, circles, and cluster numbers
            map_obj = clusterplotter(df, cluster_column, cols)

            # Add cluster numbers as HTML div icons at the center of each cluster
            unique_clusters = df[cluster_column].unique()

            for cluster in unique_clusters:

                if cluster == -1:
                    continue

                cluster_df = df[df[cluster_column] == cluster]
                cluster_lat = cluster_df['Latitude'].mean()
                cluster_lon = cluster_df['Longitude'].mean()
                cluster_html = f"""<div style="font-size: 12pt; color: black; background-color: {cols[cluster]}; 
                                    width: 30px; height: 30px; display: flex; align-items: center; 
                                    justify-content: center; border-radius: 50%; border: 2px solid black;">
                                    {cluster}
                                    </div>"""

                icon = folium.DivIcon(html=cluster_html)
                folium.Marker(location=[cluster_lat, cluster_lon], icon=icon).add_to(map_obj)

            # Save the numbered maps
            out_path = f"{numbrd_f}/{occ}"

            if not os.path.exists(out_path):
                os.makedirs(out_path)

            map_file_path = os.path.join(out_path, file_name.replace("ClusterData.csv", "") + "MapN.html")
            map_obj.save(map_file_path)


# -------------- To Generate KML for Google Earth------------------------
# import folium
# import pandas as pd
# import numpy as np
# import glob
# import os


# def hex_to_kml_color(hex_color):
#     hex_color = hex_color.lstrip('#')
#     r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
#     return 'ff' + b + g + r


# def generate_circle_points(lat, lon, radius_m, num_points=36):
#     points = []
#     R = 6371000  # Earth radius in meters
#     lat_rad = np.radians(lat)
#     lon_rad = np.radians(lon)
#     for i in range(num_points + 1):  # +1 to close the loop
#         bearing = i * 360 / num_points
#         bearing_rad = np.radians(bearing)
#         delta = radius_m / R
#         lat2_rad = np.arcsin(np.sin(lat_rad) * np.cos(delta) + np.cos(lat_rad) * np.sin(delta) * np.cos(bearing_rad))
#         lon2_rad = lon_rad + np.arctan2(np.sin(bearing_rad) * np.sin(delta) * np.cos(lat_rad),
#                                         np.cos(delta) - np.sin(lat_rad) * np.sin(lat2_rad))
#         lat2 = np.degrees(lat2_rad)
#         lon2 = np.degrees(lon2_rad)
#         points.append((lon2, lat2))
#     return points


# def clusterplotter(df, cluster_column, cols):
#     mapping = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=9, tiles="OpenStreetMap")
#     unique_clusters = df[cluster_column].unique()

#     for cluster in unique_clusters:
#         if cluster == -1:
#             cluster_color = ''
#         else:
#             cluster_color = cols[cluster]

#         cluster_df = df[df[cluster_column] == cluster]

#         cluster_lat = cluster_df['Latitude'].mean()
#         cluster_lon = cluster_df['Longitude'].mean()

#         # Calculate the distance between cluster center and farthest point
#         cluster_points = cluster_df[['Latitude', 'Longitude']].values
#         center = np.array([cluster_lat, cluster_lon]) # save the cluster long lat to csv and with cluster number
#         distances = np.linalg.norm(cluster_points - center, axis=1)
#         max_distance = np.max(distances)

#         folium.Circle(location=[cluster_lat, cluster_lon],
#                       radius=max_distance * 160000,  # Convert to meters for radius (if you want this multiply by 1000)
#                       color=cluster_color,
#                       fill=False,
#                       fill_color=cluster_color,
#                       ).add_to(mapping)

#         # Plot individual GPS points within the cluster
#         for _, row in cluster_df.iterrows():
#             folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
#                                 radius=5,
#                                 color=cluster_color,
#                                 fill=False,
#                                 fill_color=cluster_color,
#                                 ).add_to(mapping)

#     return mapping


# cols = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
#         '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff',
#         '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
#         '#000075', '#808080'] * 100

# occ_path = "../clusters"

# numbrd_f = "../numbered"

# ge_path = "../google_earth"

# for occ in os.listdir(occ_path):

#     folder_path = f"{occ_path}/{occ}"  # Path to the folder containing the cluster data CSV files

#     # Iterate over each file in the folder
#     for file_name in os.listdir(folder_path):

#         if file_name.endswith(".csv"):  # Process only CSV files

#             print(file_name)

#             file_path = os.path.join(folder_path, file_name)
#             df = pd.read_csv(file_path)

#             # Get the cluster column name
#             cluster_column = [column for column in df.columns if column.startswith("Cluster_DBSCAN")][0]

#             # Generate the map with clusters, circles, and cluster numbers
#             map_obj = clusterplotter(df, cluster_column, cols)

#             # Add cluster numbers as HTML div icons at the center of each cluster
#             unique_clusters = df[cluster_column].unique()

#             for cluster in unique_clusters:

#                 if cluster == -1:
#                     continue

#                 cluster_df = df[df[cluster_column] == cluster]
#                 cluster_lat = cluster_df['Latitude'].mean()
#                 cluster_lon = cluster_df['Longitude'].mean()
#                 cluster_html = f"""<div style="font-size: 12pt; color: black; background-color: {cols[cluster]}; 
#                                     width: 30px; height: 30px; display: flex; align-items: center; 
#                                     justify-content: center; border-radius: 50%; border: 2px solid black;">
#                                     {cluster}
#                                     </div>"""

#                 icon = folium.DivIcon(html=cluster_html)
#                 folium.Marker(location=[cluster_lat, cluster_lon], icon=icon).add_to(map_obj)

#             # Save the numbered maps
#             out_path = f"{numbrd_f}/{occ}"

#             if not os.path.exists(out_path):
#                 os.makedirs(out_path)

#             map_file_path = os.path.join(out_path, file_name.replace("ClusterData.csv", "") + "MapN.html")
#             map_obj.save(map_file_path)

#             # Generate KML for Google Earth
#             kml = '''<?xml version="1.0" encoding="UTF-8"?>
# <kml xmlns="http://www.opengis.net/kml/2.2">
# <Document>
# <name>{} Cluster Map</name>
# '''.format(occ + ' ' + file_name.replace('.csv', ''))

#             for cluster in unique_clusters:
#                 if cluster == -1:
#                     cluster_color = '#000000'
#                     folder_name = 'Noise'
#                 else:
#                     cluster_color = cols[cluster]
#                     folder_name = f'Cluster {cluster}'

#                 kml_color = hex_to_kml_color(cluster_color)

#                 cluster_df = df[df[cluster_column] == cluster]
#                 if cluster_df.empty:
#                     continue

#                 cluster_lat = cluster_df['Latitude'].mean()
#                 cluster_lon = cluster_df['Longitude'].mean()

#                 cluster_points = cluster_df[['Latitude', 'Longitude']].values
#                 center = np.array([cluster_lat, cluster_lon])
#                 distances = np.linalg.norm(cluster_points - center, axis=1)
#                 max_distance = np.max(distances)
#                 radius_m = max_distance * 160000

#                 kml += f'<Folder><name>{folder_name}</name>'

#                 if max_distance > 0:
#                     points = generate_circle_points(cluster_lat, cluster_lon, radius_m)
#                     coords = ' '.join([f"{lon},{lat},0" for lon, lat in points])
#                     kml += f'''
# <Placemark>
# <name>Cluster Boundary</name>
# <Style>
# <LineStyle><color>{kml_color}</color><width>2</width></LineStyle>
# <PolyStyle><fill>0</fill></PolyStyle>
# </Style>
# <Polygon>
# <outerBoundaryIs>
# <LinearRing>
# <coordinates>{coords}</coordinates>
# </LinearRing>
# </outerBoundaryIs>
# </Polygon>
# </Placemark>
# '''

#                 # Add points
#                 for _, row in cluster_df.iterrows():
#                     plon, plat = row['Longitude'], row['Latitude']
#                     kml += f'''
# <Placemark>
# <Style>
# <IconStyle>
# <color>{kml_color}</color>
# <scale>0.5</scale>
# <Icon><href>http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png</href></Icon>
# </IconStyle>
# </Style>
# <Point><coordinates>{plon},{plat},0</coordinates></Point>
# </Placemark>
# '''

#                 # Add label if not noise
#                 if cluster != -1:
#                     kml += f'''
# <Placemark>
# <name>{cluster}</name>
# <Style>
# <IconStyle><scale>0</scale></IconStyle>
# <LabelStyle><color>ff000000</color><scale>1.2</scale></LabelStyle>
# </Style>
# <Point><coordinates>{cluster_lon},{cluster_lat},0</coordinates></Point>
# </Placemark>
# '''

#                 kml += '</Folder>'

#             kml += '</Document></kml>'

#             # Save the KML file
#             ge_out_path = f"{ge_path}/{occ}"
#             if not os.path.exists(ge_out_path):
#                 os.makedirs(ge_out_path)

#             kml_file_path = os.path.join(ge_out_path, file_name.replace("ClusterData.csv", "") + "Cluster.kml")
#             with open(kml_file_path, 'w') as f:
#                 f.write(kml)