#! /usr/bin/env python
import os

from visualize.pcd_viewer import showObjectInPointCloud, imageSegmentationMid
from filenameparser.parser import getFileIndex, joinFilePath

def main():
    file_path, file_index_list = getFileIndex()

    for file_index in file_index_list:
        img_file_name, label_file_name, point_cloud_file_name, calib_file_name = joinFilePath(file_path, file_index)
        showObjectInPointCloud(point_cloud_file_name, label_file_name, calib_file_name)
        
if __name__ == "__main__":
    main()