import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
from itertools import permutations


def get_inter_dist(df,col):
    distm = pd.DataFrame(pairwise_distances(df.drop(col, axis = 1)),
                         index = df.index,
                         columns = df.index)

    colu = df[col].unique()
    colu = [list(items) for items in permutations(colu, r=2)]

    dist_mat_lil=[]
    for i in colu:
        i0 = df.loc[df[col] == i[0]].index.to_list()
        i1 = df.loc[df[col] == i[1]].index.to_list()
        dist_mat_lil += [i+[distm.loc[i0,i1].min().min()]]

    dist_mat_lil = pd.pivot_table(pd.DataFrame(dist_mat_lil),index = 0, columns = 1,values = 2)
    dist_mat_lil['num1'] = dist_mat_lil.index.map(lambda x: int(x[:2]) )
    dist_mat_lil['r_index'] = dist_mat_lil.index
    dind_f= pd.DataFrame(dist_mat_lil[['num1','r_index']])
    dind_f.columns = ['first','second']
    df_index = pd.MultiIndex.from_frame(dind_f)
    dist_mat_lil = dist_mat_lil.set_index(['num1','r_index'])
    dist_mat_lil.columns = df_index

    return dist_mat_lil
