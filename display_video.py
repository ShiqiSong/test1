#!/usr/bin/env python3
# -*- coding: utf-8 -*--8
import cv2


def video_process(img_list):
    """
    作用：显示最新的图片
    :param img_list: 图片队列
    """
    cv2.namedWindow("display", flags=cv2.WINDOW_FREERATIO)
    while True:
            frame = img_list.get()
            print(frame.shape)
            cv2.imshow("display", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
