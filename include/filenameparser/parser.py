import argparse
import os

def argParsing():
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_path', required=True, help="Input image directory path")
    args = parser.parse_args()

    return args.data_path

def getFileIndex():
    file_path = argParsing()

    file_index_list = list()

    img_file_list = os.listdir(file_path + "image_2")
    img_file_list.sort()

    for file_name in img_file_list:
        file_index = file_name.split('.')[0]
        file_index_list.append(int(file_index))

    return file_path, file_index_list

def joinFilePath(file_path, file_idx):

    img_file_name = os.path.join(file_path, 'image_2/{0:06d}.png'.format(file_idx))
    label_file_name= os.path.join(file_path, 'label_2/{0:06d}.txt'.format(file_idx))
    point_cloud_file_name = os.path.join(file_path, 'save/{0:06d}.bin'.format(file_idx))
    calib_file_name = os.path.join(file_path, 'calib/{0:06d}.txt'.format(file_idx))

    return img_file_name, label_file_name, point_cloud_file_name, calib_file_name