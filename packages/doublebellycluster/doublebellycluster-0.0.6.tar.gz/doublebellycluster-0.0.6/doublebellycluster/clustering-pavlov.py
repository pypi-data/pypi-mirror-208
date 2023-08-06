import copy
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, Point, MultiPoint, LineString, MultiPolygon
from shapely.ops import polygonize, unary_union
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.neighbors import KNeighborsClassifier
import alphashape


proj_wgs84 = pyproj.Proj(init="epsg:4326")
proj_gk4 = pyproj.Proj(init="epsg:20015")


loc = pd.read_csv('C:/Users/User/Desktop/dus.csv', index_col=0)
loc.columns = ['x','y', 'col']




knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(loc[['x', 'y']], loc['col'])

points = np.array(loc[['x', 'y']])

# Рассчет полигонов вороного
vor = Voronoi(points)
lines = [
    LineString(vor.vertices[line])
    for line in vor.ridge_vertices if -1 not in line
]


hull = alphashape.alphashape(points, alpha=len(points)*0.025)
hull_pts = [i.exterior.coords.xy for i in hull.geoms]
point_hull = [i for i in zip(*hull_pts)]


buf=0.001
tot_hull = Polygon(point_hull).buffer(buf)


result = [poly.intersection(tot_hull) for poly in polygonize(lines)]
result = result+ [tot_hull.difference(unary_union(result))]

# Кластеризация полигонов и объединение
u = []
for i in result:
    hull = i.convex_hull
    lo = np.dstack(hull.exterior.coords.xy).tolist()[0]
    lo = knn.predict(lo)
    u += [lo[0]]

res = []
for i in loc.col.unique():
    av = [result[k] for k, v in enumerate(u) if v == i]
    res += [unary_union(av)]

for r in res:
    plt.fill(*zip(*np.array(list(
        zip(r.boundary.coords.xy[0][:-1], r.boundary.coords.xy[1][:-1])))),
             alpha=0.4)
plt.show()

print('Poligons: \n', res)


