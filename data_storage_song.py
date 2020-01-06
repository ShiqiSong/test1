#!/usr/bin/env python3
# -*- coding: utf-8 -*--8
# 功能：将当前最新的图片与雷达数据队列中的前delay_size个数据对应并存储
import cv2, gc, os
import xlwt
import datetime, time


def data_storage_process(img_list, radar_list, start_flag):
    """
    作用：存储二者同步数据,雷达数据保存在表格里面，图像保存在同名文件夹里
    :param img_list:图像队列
    :param radar_list:雷达帧数据队列
    :param start_flag:开始存储标志（补偿二者时间差标志）
    """
    print('SubProcess %s Waiting for storage data...' % os.getpid())
    # 建立雷达表格
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('毫米波数据')
    head = ['帧ID', '跟踪的ID', '车道线', '类别', 'X', 'Y', 'Z',
            '速度', 'flag', '雷达散射截面积1', '雷达散射截面积2']
    for h in range(len(head)):  # 每个col只能写一次
        sheet.col(h).width = 4200
        sheet.write(0, h, head[h])  # print('sheet created')
    save_time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    saved_path = os.path.join(save_time)
    # saved_path = os.path.join(os.path.abspath('.'), save_time)
    os.mkdir(saved_path)  # 建立文件夹
    count = 0  # 采集图片张数
    row = 1  # 表格行数
    while True:
        if not start_flag.empty():  # 判断是否进行了延时补偿
            print("开始同步采集。。。。。。。。。。。")
            img = img_list.get()  # 提取队列中图片
            radar_frame = radar_list[0]  # radar_frame为嵌套列表，第一个元素是保存数据时系统时间戳，其余依次是各个目标雷达数据（一个目标为一个列表）
            # 将雷达数据进行进一步解析
            radar_frame_data = radar_frame[1:]  # radar_frame_data为保存多个目标的雷达数据列表
            # print("radar_frame_data：：：：", radar_frame_data)
            # 如果雷达没有检测到目标(radar_frame[1]为0)，则不执行保存操作
            if radar_frame[1] == 0:
                continue
            for radar_frame_data_index in radar_frame_data:
                device_id, track_id, triggle_flag, lane, classes = radar_frame_data_index[0], \
                                                                   radar_frame_data_index[1], radar_frame_data_index[8], \
                                                                   radar_frame_data_index[9], \
                                                                   radar_frame_data_index[10]
                loc_x, loc_y, loc_z, speed = round(radar_frame_data_index[2], 5), \
                                             round(radar_frame_data_index[3], 5), \
                                             round(radar_frame_data_index[4], 5), abs(
                    round(radar_frame_data_index[5], 3))
                rcs1, rcs2 = radar_frame_data_index[6], radar_frame_data_index[7]
                sheet.write(row, 0, count)
                sheet.write(row, 1, track_id)
                sheet.write(row, 2, lane)
                sheet.write(row, 3, classes)
                sheet.write(row, 4, loc_x)
                sheet.write(row, 5, loc_y)
                sheet.write(row, 6, loc_z)
                sheet.write(row, 7, speed)
                sheet.write(row, 8, triggle_flag)
                sheet.write(row, 9, rcs1)
                sheet.write(row, 10, rcs2)
                row += 1
                workbook.save('{}.xls'.format(save_time))  # 保存雷达数据，每次采集的数据都保存在同一个表格里
            img_name = str(count) + '.jpg'
            picture_path = os.path.join(saved_path, img_name)
            print(picture_path)
            cv2.imwrite(picture_path, img)  # 保存图像
            count += 1
