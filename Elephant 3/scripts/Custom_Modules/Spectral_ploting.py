import SpectralClustering
from sklearn.cluster import KMeans

n_clusters=4
sigma=6

data_points=[[]]
# Perform k-means clustering on the eigen vector space
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
kmeans.fit(eigVec)

# Get cluster labels and centroids
cluster_labels = kmeans.labels_
centroids = kmeans.cluster_centers_

# # Plot the data points and cluster centers
# plt.figure(figsize=(8, 6))
#
# # Plot data points
plt.scatter(data_points[:, 0], data_points[:, 1], c=cluster_labels, cmap='viridis', edgecolors='k', s=50)
# plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroids')
#
# plt.title('K-means Clustering')
# plt.xlabel('Feature 1')
# plt.ylabel('Feature 2')
# plt.legend()
# plt.show()

# # Print results
# print("Cluster Labels:", cluster_labels)
# print("Centroids:", centroids)
