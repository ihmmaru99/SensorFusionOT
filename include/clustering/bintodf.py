import struct
import sys
from struct import unpack
import pandas as pd
import numpy as np

def readBinFile(file_name):
    np_pcd = np.fromfile(file_name, dtype=np.float32).reshape((-1, 3))
    np_pcd = np_pcd[:, :3]

    df = pd.DataFrame(np_pcd, columns = ['x', 'y', 'z'])

    print(df.head())
    return df