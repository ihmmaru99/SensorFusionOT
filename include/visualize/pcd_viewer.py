#! /usr/bin/env python

import numpy as np
import os, math
import pptk

from clustering.clustering import DBScan
global object_list
object_list = []

# image border width
BOX_BORDER_WIDTH = 5

# point size
POINT_SIZE = 0.005

MARKER_COLOR = {
    'IDontknow': [0, 0, 0],
    'car': [1, 0, 0],               # red
    'NonMovable': [0, 0, 0.5],          # black
    'person': [0, 0, 1],        # blue
    'bus': [1, 1, 0],               # yellow
    'motorcycle': [1, 0, 1],           # magenta
}

def imageSegmentationMid(label_filename, calib_filename):
    result = []
    calib = loadKittiCalib(calib_filename)
    with open(label_filename) as f_label:
        lines = f_label.readlines()
        for line in lines:
            line = line.strip('\n').split()
            object_type = line[0]
            t_lidar = cameraCoordinateToPointCloud(line[11:14], calib['Tr_velo_to_cam'])
            img_x = t_lidar[0][0]
            img_y = t_lidar[0][1]
            img_z = t_lidar[0][2]
            result.append([object_type, img_x, img_y])
    result.sort(key = lambda x : x[0])
    return result

def lidarClusterMid(pcd_data):
    pcd_data = pcd_data.values.tolist()
    pcd_data.sort(key= lambda x : x[3])
    detecting_result = list()
    nonmovable_result = list()
    dic = dict()
    for data in pcd_data:
        x = data[0]
        y = data[1]
        z = data[2]
        label = data[3]
        if label in dic:
            dic[label].append([x,y,z])
        else:
            dic[label] = [[x,y,z]]
    for key in dic:
        data = dic[key]
        length = len(data)
        data = np.array(data).T
        if len(data[0]) <= 400 and len(data[0]) > 20:
            x_avg = sum(data[0])/length
            y_avg = sum(data[1])/length
            detecting_result.append([key, x_avg, y_avg])
        else:
            nonmovable_result.append(key)
    detecting_result.sort(key = lambda x : x[0])
    print("LIDAR_CLUSTERING")
    print(len(detecting_result))
    return detecting_result, nonmovable_result

def cameraCoordinateToPointCloud(box3d, Tr):
    """
    This script is copied from https://github.com/AI-liu/Complex-YOLO
    """
    def project_cam2velo(cam, Tr):
        T = np.zeros([4, 4], dtype=np.float32)
        T[:3, :] = Tr
        T[3, 3] = 1
        T_inv = np.linalg.inv(T)
        lidar_loc_ = np.dot(T_inv, cam)
        lidar_loc = lidar_loc_[:3]
        return lidar_loc.reshape(1, 3)

    tx, ty, tz = [float(i) for i in box3d]
    cam = np.ones([4, 1])
    cam[0] = tx
    cam[1] = ty
    cam[2] = tz
    t_lidar = project_cam2velo(cam, Tr)

    # t_lidar: the x, y coordinator of the center of the object
    return t_lidar

def compareLidarImagePoints(lidar_points, image_points):
    global object_list
    result = []
    midPointResult = []
    filteringMidData = []
    
    if len(object_list) == 0:
        object_list = image_points
    else:
        for i in range(len(image_points)):
            img_type = image_points[i][0]
            img_x = float(image_points[i][1])
            img_y = float(image_points[i][2])
            last_distance = 100000
            change = False
            for j in range(len(object_list)):
                object_type = object_list[j][0]
                object_x = object_list[j][1]
                object_y = object_list[j][2]
                distance = math.sqrt(math.pow(img_x-object_x,2)+math.pow(img_y-object_y, 2))
                if distance <= 15 and distance <= last_distance:
                    last_distance = distance
                    object_list[j] = image_points[i]
                    change = True
            if change == False:
                object_list.append(image_points[i])
    for lidar_point in lidar_points:
        lidar_idx = lidar_point[0]
        lidar_x = lidar_point[1]
        lidar_y = lidar_point[2]
        result_type = 'IDontknow'
        result_idx = lidar_idx
        last_distance = 100000
        for object_data in object_list:
            object_type = object_data[0]
            img_x = float(object_data[1])
            img_y = float(object_data[2])
            distance = math.sqrt(math.pow(lidar_x-img_x,2)+math.pow(lidar_y-img_y, 2))
            if(distance <= 5 and distance <= last_distance):
                result_idx = lidar_idx
                result_type = object_type
                last_distance = distance
        if result_type == 'IDontknow' and lidar_x >= 5:
            result_type = 'NonMovable'
        result.append([result_idx, result_type])
        midPointResult.append([result_type, lidar_x, lidar_y])

    for data in midPointResult:
        if data[0] == 'IDontknow':
            continue            
        else:
            filteringMidData.append(data)

    object_list = filteringMidData
                
    print("OBJECT LIST SIZE : ", len(object_list))
    print(object_list)
    return result, filteringMidData

def showObjectInPointCloud(point_cloud_file_name, label_file_name, calib_file_name):
    pcd_data, n_label = DBScan(point_cloud_file_name)
    np_pcd_data = pcd_data.to_numpy()
    movable_lidar_points, nonmovable_lidar_points = lidarClusterMid(pcd_data)
    image_points = imageSegmentationMid(label_file_name, calib_file_name)
    clustering_result, midPointResult = compareLidarImagePoints(movable_lidar_points, image_points)
    pc_color = np.ones((len(pcd_data), 3))
    pcd_data = pcd_data.values.tolist()
    for clustering_data in clustering_result:
        point_color = MARKER_COLOR[clustering_data[1]]
        for i, v in enumerate(pcd_data):
            if pcd_data[i][3] == clustering_data[0]:
                pc_color[i,:] = point_color
            elif pcd_data[i][3] in nonmovable_lidar_points:
                pc_color[i,:] = MARKER_COLOR['NonMovable']
    
    v = pptk.viewer(np_pcd_data[:, :3], pc_color)
    v.set(point_size=POINT_SIZE, lookat=(0,0,0), theta=np.pi/2, phi=np.pi, r = 100)
    v.wait()
    v.close()

def loadKittiCalib(calib_file):
    """
    This script is copied from https://github.com/AI-liu/Complex-YOLO
    """
    with open(calib_file) as f_calib:
        lines = f_calib.readlines()

    P0 = np.array(lines[0].strip('\n').split()[1:], dtype=np.float32)
    P1 = np.array(lines[1].strip('\n').split()[1:], dtype=np.float32)
    P2 = np.array(lines[2].strip('\n').split()[1:], dtype=np.float32)
    P3 = np.array(lines[3].strip('\n').split()[1:], dtype=np.float32)
    R0_rect = np.array(lines[4].strip('\n').split()[1:], dtype=np.float32)
    Tr_velo_to_cam = np.array(lines[5].strip('\n').split()[1:], dtype=np.float32)
    Tr_imu_to_velo = np.array(lines[6].strip('\n').split()[1:], dtype=np.float32)

    return {'P0': P0, 'P1': P1, 'P2': P2, 'P3': P3, 'R0_rect': R0_rect,
            'Tr_velo_to_cam': Tr_velo_to_cam.reshape(3, 4),
            'Tr_imu_to_velo': Tr_imu_to_velo}

if __name__ == "__main__":
    # updates
    IMG_DIR = 'C:/Users/HP/Desktop/ws/final_project/detect3d/dataset/KITTI/testing/00/image_2'
    LABEL_DIR = 'C:/Users/HP/Desktop/ws/final_project/detect3d/dataset/KITTI/testing/00/label_2'
    POINT_CLOUD_DIR = 'C:/Users/HP/Desktop/ws/final_project/detect3d/dataset/KITTI/testing/00/save'
    CALIB_DIR = 'C:/Users/HP/Desktop/ws/final_project/detect3d/dataset/KITTI/testing/00/calib'

    # id for viewing
    file_idx = 0

    img_filename = os.path.join(IMG_DIR, '{0:06d}.png'.format(file_idx))
    label_filename = os.path.join(LABEL_DIR, '{0:06d}.txt'.format(file_idx))
    pc_filename = os.path.join(POINT_CLOUD_DIR, '{0:06d}.bin'.format(file_idx))
    calib_filename = os.path.join(CALIB_DIR, '{0:06d}.txt'.format(file_idx))

    showObjectInPointCloud(pc_filename, label_filename, calib_filename)

