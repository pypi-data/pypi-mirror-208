
import copy
import numpy as np
import numpy as np
import pandas as pd

import scipy.stats as st
from sklearn.cluster import DBSCAN
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics.pairwise import pairwise_distances
 
import itertools

from .inter_dist import get_inter_dist
from .plots import plot_color_map, d3_color_map

import os
import warnings

warnings.filterwarnings("ignore")


class Doubleclustering:

    def __init__(self, showing_all = False):
        self.working = True
        self.eps = 0.015
        self.showing_all = showing_all
        dir = os.getcwd()
        print(dir)
        if 'pic' not in os.listdir(dir):
            os.makedirs(os.path.join(dir,'pic'))

        self.dir = os.path.join(dir,'pic')


    def d3plot(self, xy):


        D = xy.shape[1]

        self.D = D

        if D==3:
            self.eps = 0.05
    
        xy.columns=list(range(D))

        for i in xy.columns:
            xy[i] = xy[i].to_list()
        
        xy -= xy.min()
        xy /= xy.max()

        # getting xy
        self.xy = xy

        n100 = min(10**(5/D),100)
        
        n_bins =  n100*np.ones(D)
        bounds = np.repeat([(0,1)], D, axis = 0)

        result = np.mgrid[[slice(row[0], row[1], n*1j) for row, n in zip(bounds, n_bins)]]

        positions = np.vstack([i.ravel() for i in result])
        values = np.vstack([xy[i] for i in xy.columns])
        kernel = st.gaussian_kde(values)
        print(result[0].shape)
        f = kernel(positions).T
        
        def make_profii(k):
            a=[]
            num_dan = np.arange(0,D)[::-1]
            for j in num_dan:
                a += [k//(n100**j)]
                k =k%(n100**j)
            return a

        fs = [make_profii(k)+[i] for k, i in enumerate(f)]
        fs = pd.DataFrame(fs, columns=list(range(D))+['f'])
        fs = fs.sort_values('f',ascending=False)

        fs[list(range(D))] /=n100
        
        Knn = KNeighborsClassifier(n_neighbors=10)
        Knn.fit(fs[range(D)], fs.index)
        lobl = Knn.predict(xy)
        unique, counts = np.unique(lobl, return_counts=True)

        fs['len'] = fs.index.map(dict(zip(unique, counts)))

        fs = fs.dropna()

        fs.f -= fs.f.min()
        fs.f /= fs.f.max()
        fs.f *= 100

        self.fs = fs

        
    def do_fs_beer(self):

        fs = self.fs

        d_mat =pairwise_distances(fs[list(range(self.D))])

        eps = fs[range(self.D)].std(0).diff().min()*2
        print(eps)

        c = 100
        height = 5
        dbs = DBSCAN(eps= self.eps, min_samples=1)
        fs['l']=-1
        fs['l1']=-1
        while c > 5:

            fs1 = fs.loc[fs.f > c - height]
            dbs = dbs.fit(fs1[range(self.D)])
            fs.loc[fs1.index,'l'] = dbs.labels_

            a_get0 = fs.loc[fs1.index].groupby('l')['l1'].unique().reset_index()
            a_get0['l1'] = a_get0['l1'].map(lambda x: list(x))
            a_get0['1']=a_get0['l1'].map(lambda x: len([i for i in x if i!=-1 ]))
            a_get0 = list(itertools.chain(*a_get0.loc[a_get0['1'] >= 2, 'l1'].to_list()))
            a_get0 = [i for i in a_get0 if i != -1]
            a_get1 = fs.loc[fs1.index].groupby('l1')['l'].count()
            a_get1 = fs.loc[fs1.index].groupby('l1').apply(lambda x: pd.Series({
                'len': x['len'].sum()
                # ,'mind '+str(c): d_mat.loc[x.index, x.index].min().max() + 2 * d_mat.loc[x.index, x.index].min().std()
            }))

            a_get1 = a_get1.loc[a_get1['len']>50]
            a_get1 = a_get1.drop('len', axis=1)
            a_get1 = a_get1.loc[a_get1.index.isin(a_get0)]

            if len(a_get1) > 0:
                fs = fs.merge(a_get1, on = ['l1'], how = 'left')
                fs['col '+ str(c)] = np.nan
                fs.loc[fs['l1'].isin(a_get1.index),  'col ' + str(c)] = fs.loc[fs['l1'].isin(a_get1.index),'l1']

            fs['l1'] = copy.deepcopy(fs['l'])
            c -= height

        fs = fs.drop(['l','l1'],axis=1)

        self.fs = fs




    def fs_regress_allneed(self):

        fs = self.fs

        d_framedata = fs.iloc[:,self.D + 2:]
        col = d_framedata.columns
        d_framedata = d_framedata[[i for i in col if 'col' in i]]
        for i in range(0,d_framedata.shape[1]-1):
            re = list(d_framedata.iloc[:,i].dropna().index)

            for jj in range(i+1,d_framedata.shape[1]):

                a_var_step1 = list(d_framedata.iloc[re,jj].unique())
                promejutoc_var = d_framedata.iloc[:, jj]
                promejutoc_var[promejutoc_var.isin(a_var_step1)]=np.nan
                d_framedata.iloc[:, jj] = promejutoc_var

        col = d_framedata.columns
        def get_h_done(x):
            x_k = np.where(x >= 0)[0]
            if len(x_k)>0:
                k = min(list(x_k))
                res = [int(col[k].split(' ')[1]), x[k]]
            else:
                res = [np.nan]*2
            return res
        

        det_matrix = pd.DataFrame( np.array( d_framedata.apply(lambda x: get_h_done(x), axis =1).to_list()),
                                  columns = ['level','cl'])
        
        fs = fs.join(det_matrix)
        fs['fin_join'] = det_matrix.astype(str).apply(lambda x: '-'.join(x), axis =1)
        fs = fs.sort_values(['level','cl'])
        fs_to_plot = fs.loc[fs['fin_join']!='nan-nan']

        self.fs = fs
        self.fs_to_plot = fs_to_plot

        

    def do_color_cluster(self):

        fs_to_plot = self.fs_to_plot

        dist_mat_lil = get_inter_dist(fs_to_plot[list(range(self.D))+['fin_join']],'fin_join')
        fs_resullt = fs_to_plot.groupby(['level','fin_join'])['len'].sum().reset_index()

        num_dic={i:k for k,i in enumerate(fs_to_plot['level'].unique())}

        dd= {}
        for i in range(len(fs_resullt)):

            dd_dicccy=list(dd.keys()) + list(dd.values())
            read_file = fs_resullt.loc[i,]
            idx = pd.IndexSlice
            d_ma = dist_mat_lil.loc[idx[:, read_file['fin_join']],:].dropna(1)
            d_ma = d_ma.sort_values(d_ma.index[0], axis =1).iloc[:,:4]
            from_ = [i[1] for i in d_ma.columns if i[0]==read_file[0]]
            d_ma = d_ma.loc[:, idx[:,from_]]
            
            if d_ma.shape[1]:
                ind = d_ma.columns[0][1]
            else:
                ind = read_file['fin_join'] 

            if read_file['fin_join'] not in dd_dicccy:
                dd[read_file['fin_join']] = ind

        
        for i in dd_dicccy:
            if i not in dd.keys():
                dd[i] = i


        fs_to_plot['fin_join'] = fs_to_plot['fin_join'].map(dd)   ##
        self.fs_to_plot = fs_to_plot



    def do_model_clusterspare(self, percentile_cut):

        fs_to_plot = self.fs_to_plot
        fs = self.fs

        fs = fs.drop(['fin_join'],axis=1).merge(fs_to_plot[list(range(self.D))+['fin_join']], on = list(range(self.D)), how = 'left')
        llist = list(fs.loc[fs['fin_join'].isna()==False,'level'].unique()[::-1]) +[0.]
        fs['level'] = fs['f'].map(lambda x: max([i for i in llist if i<= int(x)]))
        for i in llist:
            x = fs.loc[(fs['level']>=i)&(fs['fin_join'].isna()==False)]
            Knn = KNeighborsClassifier(n_neighbors=2)
            Knn.fit(x[list(range(self.D))], x['fin_join'])
            print(i)
            if len(fs.loc[(fs['level']>=i)&(fs['fin_join'].isna()), 'fin_join']):
                fs.loc[(fs['level']>=i)&(fs['fin_join'].isna()), 'fin_join'] = Knn.predict(fs.loc[(fs['level']>=i)&(fs['fin_join'].isna()), list(range(self.D))])

        fs['col'] = fs['fin_join'].map({i:k+1 for k,i in enumerate(fs['fin_join'].unique())})

        self.fs = fs
        self.fs_to_plot = fs.loc[fs['level']>=percentile_cut]


    def end(self):

        fs_to_plot = self.fs_to_plot
        xy = self.xy
           
        Knn = KNeighborsClassifier(n_neighbors=10)
        Knn.fit(fs_to_plot[list(range(self.D))], fs_to_plot['fin_join'])
        xy[ 'fin_join'] = Knn.predict(xy[list(range(self.D))])
        xy['col'] = xy['fin_join'].map({i:k+1 for k,i in enumerate(xy['fin_join'].unique())})

        self.xy = xy


    def do_continis(self, xy,
                      calc_aggregate_all= False,
                      percentile_cut = 10):

        if xy.isna().sum().sum()==0:
            pass
        else:
            raise ValueError('Nan is presutstvoble')

        if xy.shape[1]>1 and xy.shape[1]<4 :
            pass
        else:
            raise ValueError('Non number of variables')
        
        if xy.dtypes.astype(str).map(lambda x: 'int' in x or 'float' in x).all():
            pass
        else:
            raise ValueError('Non doooable types.')

        if percentile_cut >= 0 and percentile_cut <= 100:
            pass
        else:
            raise ValueError('Bad percentile cut')

        self.d3plot(xy)
        self.do_fs_beer()
        self.fs_regress_allneed()

        if self.showing_all: plot_color_map(self.fs_to_plot[[0,1,'fin_join']],
                       self.dir + '/first_exampl', show_save = False)

        if calc_aggregate_all:
            self.do_color_cluster()
            # aggregate clusters all
            if self.showing_all: plot_color_map(self.fs_to_plot[[0, 1 ,'fin_join']],
                       self.dir + '/second_exampl', show_save = False)

                
        self.do_model_clusterspare(percentile_cut)

        if self.showing_all: plot_color_map(self.fs_to_plot[[0, 1 ,'fin_join']], 
                       self.dir + '/third_exampl', show_save = False)

        self.end()

        return self.xy[ 'col']
        

    def d3_color_map(self, folder='', show_save = False):
        if self.showing_all:
            folder = self.dir
        if hasattr(self, 'fs'):
            return d3_color_map(self.fs, folder + '/d3_color', show_save)
        else:
            raise ValueError('Not ccounted yet')

    def show_fi_plot_(self, folder='', show_save = False):
        if self.showing_all:
            folder = self.dir
        if 'fin_join' in self.xy.columns:
            return plot_color_map(self.xy[[0, 1 ,'fin_join']], 
                       self.dir + '/data_exampl', show_save)
        else:
            raise ValueError('Not ccounted yet')

        

if __name__ == '__main__':
    

    showing_all = True

    import pyproj
    proj_wgs84 = pyproj.Proj(init="epsg:4326")
    proj_gk4 = pyproj.Proj(init="epsg:20015")


    xy = pd.read_csv('C:/Users/User/Desktop/accidents.csv').iloc[:1000000]

    xy['xx'], xy['yy'] = pyproj.transform(proj_wgs84, proj_gk4, xy['lon'].values,
                                                        xy['lat'].values)

    xy['xy'] = np.sin(xy['xx'])

    xy = xy.loc[xy['Local_Authority_(District)']==12]

    doubleclustering = Doubleclustering(showing_all)

    doubleclustering.eps = 0.015


    xy['col'] = doubleclustering.do_continis( xy[['xx', 'yy']],
                        calc_aggregate_all= True,
                        percentile_cut = 10)

    doubleclustering.d3_color_map(folder='C:/Users/User/Desktop',show_save = False)

    doubleclustering.show_fi_plot_(folder='C:/Users/User/Desktop',show_save = False)

    print(xy)


