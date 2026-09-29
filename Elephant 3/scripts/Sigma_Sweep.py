
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go
from Custom_Modules.SpectralClustering import *
import numpy as np
import os


def compute_EigenGap_Clusters(eigen_values, n, m):
    sorted_eigen_values = np.sort(eigen_values)
    gap = sorted_eigen_values[m - 1] - sorted_eigen_values[n - 1], n
    #gap = np.log(gap)
    return gap


# ----------------------- Convert string data into numerical values ----------------------------------------------------


enc = 'BinaryZones'
# enc = 'Regular'

# lap = 'UL'
lap = 'SNL'
# lap = 'RWL'

max_sigma = 20
self_similarity = 1
targets = ['\\dc']

data_labels, data_points = get_multipleClass_StringData(classes=targets, encoding=enc)

# print(data_points)

sigmaX = np.linspace(0.1, max_sigma, max_sigma * 10)

y_2_3 = np.zeros(len(sigmaX))
y_3_4 = np.zeros(len(sigmaX))
y_4_5 = np.zeros(len(sigmaX))
y_5_6 = np.zeros(len(sigmaX))
# print(sigmaX)
i = 0
for sigma in sigmaX:
    [eigVal, eigVec] = spectral_Clustering_Eigen_Decompose(data_labels, data_points, sigma, selfSimilarity=self_similarity,
                                                           laplacian=lap)
    eigVal = np.real(eigVal)
    eigVec = np.real(eigVec)
    [Gap2_3, clusters2] = compute_EigenGap_Clusters(eigVal, 2, 3)
    [Gap3_4, clusters3] = compute_EigenGap_Clusters(eigVal, 3, 4)
    [Gap4_5, clusters4] = compute_EigenGap_Clusters(eigVal, 4, 5)
    [Gap5_6, clusters5] = compute_EigenGap_Clusters(eigVal, 5, 6)

    y_2_3[i] = Gap2_3
    y_3_4[i] = Gap3_4
    y_4_5[i] = Gap4_5
    y_5_6[i] = Gap5_6
    i += 1

# print(y)

title = 'SS='+str(self_similarity)+'_Classes_ '

for i in targets:
    title += i[1:] + ' '

plt.plot(sigmaX, y_2_3)
plt.plot(sigmaX, y_3_4)
plt.plot(sigmaX, y_4_5)
plt.plot(sigmaX, y_5_6)
plt.legend(['mode 23', 'mode 34', 'mode 45', 'mode 56'])

plt.grid()
# plt.title(enc +' Encoding, Laplacian = ' + lap)
plt.title(title)
plt.xlabel("Sigma")
plt.ylabel("Eigen Gap")
plt.show()

fig = go.Figure()

fig.add_trace(go.Scatter(x=sigmaX, y=y_2_3, name='mode 23'))
fig.add_trace(go.Scatter(x=sigmaX, y=y_3_4, name='mode 34'))
fig.add_trace(go.Scatter(x=sigmaX, y=y_4_5, name='mode 45'))
fig.add_trace(go.Scatter(x=sigmaX, y=y_5_6, name='mode 56'))

fig.update_layout(xaxis_title="Sigma",
                  yaxis_title="Eigen gap",
                  legend_title="LEGEND",
                  title=dict(text=title, font=dict(size=50))
                  )

# print(os.path.abspath(os.curdir))

save_loc = "./Results/SigmaSweep"

if not os.path.exists(save_loc):
    os.makedirs(save_loc)

# plotly.offline.plot(fig, filename='X:\\PROJECTS\\FYP\\ai4covid_clustering\\Results\\Sigma Sweep\\'+title+'.html', auto_open=False)

plotly.offline.plot(fig, filename=f"{save_loc}/{title}.html", auto_open=False)

fig.show()
