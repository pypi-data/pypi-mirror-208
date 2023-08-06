
import math

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
import random
import os

from plots import plot_color_map

import warnings
warnings.filterwarnings("ignore")



def do_nearby_cluster(check_array, xy, ):

    sub_deveied_data = xy.groupby('y')[[0,1]].mean().reset_index()
    xy = pd.concat([xy,sub_deveied_data],axis = 0)

    print(xy)

    nun = xy['y'].nunique()
    d_matrix = pd.DataFrame(pairwise_distances(xy[[0,1]].iloc[-nun:,:],xy[[0,1]].iloc[:-nun,:]) )
    print(d_matrix)


    d = [[] for i in range(nun)]
    count =0 
    while count < xy.shape[0] - sub_deveied_data.shape[0]:
        
        if count%100 == 0:
            num_array =[]
            for i in range(nun):
                num_array += [len(d[i])]
            num_array = np.array(num_array)
            num_array = num_array / num_array.sum()

            n_where_num = num_array - check_array <= -0.01
            

            if sum(n_where_num) == 0:
                n_where_num[random.randrange(nun)] = True
            print(int(count/xy.shape[0]*100))
            

        for i in range(nun):
            if n_where_num[i]:
                ind = d_matrix.iloc[i,:].idxmin()
                if math.isnan(ind) == False:
                    d[i] += [ind]
                    d_matrix.iloc[:,ind]= np.nan

                    count +=1
        
    num_array =[]
    for i in range(nun):
        num_array += [len(d[i])]
    num_array = np.array(num_array)
    num_array = num_array / num_array.sum()
    print(num_array)

    col = [[k for k, j in enumerate(d) if i in j][0] for i in range(xy.shape[0]-3)]
    
    return col



if __name__ == '__main__':
    


    import pyproj
    proj_wgs84 = pyproj.Proj(init="epsg:4326")
    proj_gk4 = pyproj.Proj(init="epsg:20015")

    xy = pd.read_csv('C:/Users/User/Desktop/yyy.csv', index_col=0)[['lat','lon']].iloc[:10000]


    xy[0], xy[1] = pyproj.transform(proj_wgs84, proj_gk4, xy['lon'].values,
                                                            xy['lat'].values)

    from sklearn.cluster import AgglomerativeClustering

    xy['y'] = AgglomerativeClustering(n_clusters=3).fit_predict(xy[[0,1 ]] )

    plot_color_map(xy[[0,1,'y']],  os.getcwd()+'/pic/data1', False)

    check_array = np.array([0.4, 0.5, 0.1])


    xy['fin_join'] = do_nearby_cluster(check_array, xy)

    plot_color_map(xy[[0,1,'fin_join']],  os.getcwd()+'/pic/data2', False)


