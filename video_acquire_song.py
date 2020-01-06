#!/usr/bin/env python3
# -*- coding: utf-8 -*--8
#功能：获得最新的视频图像存入列表
#保证图像列表里面包含最新图像
import cv2, time,os
def video_acquire(img_list):
    print('SubProcess %s get ready to acquire video' % os.getpid())
    try:
        cap = cv2.VideoCapture("rtsp://192.168.2.12:5454/live.h264")
        # cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print('camera is opened')
        while True:
            # _, img = cap.read()  # cap.read 6毫秒 记时到读取30毫秒如果新建文件夹的话 正常8毫秒
            # if _:
            #     img_list.append(img) #持续存入最新图片
            #     if len(img_list) >=5: #手动清理内存垃圾，防止内存溢出
            #         print("溢出")
            #         del img_list[0:4]
            #         gc.collect()
            img_list.put(cap.read()[1])
            img_list.get() if img_list.qsize() > 1 else time.sleep(0.001)
    finally:
        print("camera error")
        cap.release()
