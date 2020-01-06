#!/usr/bin/env python3
# -*- coding: utf-8 -*--8
from song.radar_data_acquire_song import Rada_acquire
from song.video_acquire_song import video_acquire
from song.data_storage_song import data_storage_process
import multiprocessing as mp
from song.display_video import video_process
import gc

if __name__ == '__main__':
    flag_queue = mp.Queue(maxsize=1)
    radar_list = mp.Manager().list()
    img_list = mp.Queue(maxsize=2)
    try:
        #开启多个进程
        get_radar_process = mp.Process(target=Rada_acquire,
                                    args=(radar_list, flag_queue), name='radar_data_acquire')
        get_video_process = mp.Process(target=video_acquire,
                                    args=(img_list,), name='video_date_acquire')
        display_video_process = mp.Process(target=video_process,
                                         args=(img_list,), name='video_date_display')
        storage_data_process = mp.Process(target=data_storage_process,
                                       args=(img_list, radar_list, flag_queue), name='storage_data')

        get_radar_process.start()
        get_video_process.start()
        display_video_process.start()
        storage_data_process.start()
        get_radar_process.join()
        get_video_process.join()
        display_video_process.join()
        storage_data_process.join()
    except KeyboardInterrupt as e:
        del radar_list, img_list, flag_queue
        gc.collect()
    finally:
        print('both process is ended')
