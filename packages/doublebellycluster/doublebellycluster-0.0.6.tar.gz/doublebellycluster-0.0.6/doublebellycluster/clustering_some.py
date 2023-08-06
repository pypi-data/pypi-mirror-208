

# функция кластеризации - считает кластеры до тех пор, пока наибольший кластер не станет по размеру менее чем
# заданное число
def make_cl(self, idx):

        loc_mest = self.location.loc[idx]

        dbs = DBSCAN(eps=5000, min_samples=10, metric='precomputed')
        loc_mest['col'] = dbs.fit_predict(self.d_matrix.loc[idx, idx])
        self_study = loc_mest.loc[loc_mest['col'] >= 0]
        knn = KNeighborsClassifier()
        knn.fit(self_study[['x', 'y']], self_study['col'])
        loc_mest.loc[loc_mest['col'] == -1, 'col'] = knn.predict(
            loc_mest.loc[loc_mest['col'] == -1, ['x', 'y']])

        class_distribution = loc_mest.groupby('col').apply(lambda x: x.index.to_list()).to_list()

        return class_distribution