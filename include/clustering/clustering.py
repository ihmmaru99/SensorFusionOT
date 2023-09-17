#! /usr/bin/env python

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from clustering.bintodf import readBinFile

def DBScan(file_name):
    """
    ### input
    bin file path

    ### output
    [0]: DataFrame[x, y, z, label]
    [1]: count unique label vlaue
    """
    pcd_df = readBinFile(file_name)
    head_data = pcd_df[['x','y']]

    scaler = StandardScaler()
    df_scaler = pd.DataFrame(scaler.fit_transform(pcd_df[['x', 'y']]), columns=head_data.columns)

    model = DBSCAN(eps=0.04, min_samples=8)
    model.fit(df_scaler)
    df_scaler['label'] = model.fit_predict(df_scaler)

    pcd_df['label'] = df_scaler['label']

    n_label = df_scaler['label'].nunique()

    return pcd_df, n_label

def getClusterCenter(pcd_df, n_label):
    """
    ### output
    cluster center(numpy array)
    """
    labels = pcd_df['label'].unique()
    cluster_center = np.zeros((n_label-1, 1, 4))
    label_count = np.zeros(n_label-1)

    for idx, row in pcd_df.iterrows():
        if int(row['label']) != -1:
            cluster_center[int(row['label'])] += np.array([row['x'], row['y'], row['z'], 0])
            label_count[int(row['label'])] += 1

    for i in range(n_label - 1):
        cluster_center[i] = cluster_center[i] / label_count[i]

    print(label_count)

    return cluster_center

if __name__ == '__main__':
    # testing
    file_name = "C:/Users/HP/Desktop/ws/final_project/detect3d/dataset/KITTI/testing/00/save/000000.bin"

    pcd_df, n_label = DBScan(file_name)
    getClusterCenter(pcd_df, n_label)