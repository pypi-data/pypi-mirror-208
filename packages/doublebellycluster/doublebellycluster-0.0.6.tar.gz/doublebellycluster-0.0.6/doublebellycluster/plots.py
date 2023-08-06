
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_color_map( df, name, show_save = True):
    fig, ax = plt.subplots()
    scatter_x = np.array(df.iloc[:,0])
    scatter_y = np.array(df.iloc[:,1])
    group = np.array(df.iloc[:,2])

    for g in np.unique(group):
        i = np.where(group == g)
        ax.scatter(scatter_x[i], scatter_y[i], label=g)
    ax.legend()
    
    if show_save:
        plt.show()
    else:
        fig.savefig(name+'.png')


def d3_color_map( fs, name, show_save = True):
    
    fs_table = pd.pivot_table(fs, index= fs[0], columns = fs[1], values = 'f').fillna(0)
    X = np.array(fs_table.index)
    Y = np.array(fs_table.columns)
    X, Y = np.meshgrid(X, Y)
    Z = np.array(fs_table.T)
    
    fs_table = np.array(pd.pivot_table(fs, index= fs[0], 
                        columns = fs[1], values = 'col').T)/10

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    my_col = cm.jet(fs_table)
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors = my_col,
            linewidth=0, antialiased=False)


    if show_save:
        plt.show()
    else:
        fig.savefig(name+'.png')
