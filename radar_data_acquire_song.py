#!/usr/bin/env python3
# -*- coding: utf-8 -*--8
from struct import *
import datetime
from socket import *
import os
import gc
from copy import deepcopy


def Rada_acquire(Radar_list, start_storage_flag):
    # 输入参数 Radar_list为存储雷达数据帧的列表，start_storage_flag达到delay_size标志为1 代表可以开始采集
    delay_size = 20  # 补偿摄像头延时雷达数据需要向前寻找帧数
    # 创建socket，以IPV4、TCP流的方式建立socket
    tcp_server_socket = socket(AF_INET, SOCK_STREAM)
    # 服务器监听地址和端口号，端口号小于1024属于标准协议80：Web服务 25：SMTP 21：FTP
    address = ('192.168.2.100', 10000)
    tcp_server_socket.bind(address)
    tcp_server_socket.listen(1)  # 等待连接的最大数量，即一个服务器对应几个客户端
    # 使用socket创建的套接字默认的属性是主动的，使用listen将其变为被动的，这样就可以接收别人的链接了
    print('SubProcess %s Waiting for radar server connection...' % os.getpid())
    # 如果有新的客户端来链接服务器，那
    #
    #
    #
    # 么就产生一个新的套接字专门为这个客户端服务
    # client_socket用来为这个客户端服务
    # tcp_server_socket就可以省下来专门等待其他新客户端的链接
    sock, sock_addr = tcp_server_socket.accept()
    print('SubProcess %s got the date for radar in %s' % (os.getpid(), sock_addr))
    # 建立连接后，持续开始读取数据
    while True:
        # print('持续接收packet')
        packet_head = sock.recv(2)  # 获取每个packet的前两个字节,用于判断属于哪个packet
        if len(packet_head) == 0:
            print("Radar clien disconnected from the server")
            break  # the clien disconnected from the server
        if packet_head[0] == 0x01 and packet_head[1] == 0x01:  # get time packet
            print('time is checking , localtime ===>>> terminal !')
            get_time_packet_data = sock.recv(5)
            if get_time_packet_data[3] == 0xFF and get_time_packet_data[4] == 0xAE:
                send_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('ascii')
                sock.send(send_time)
                print('time is checked , terminal ==>> local !')

        elif packet_head[0] == 0x01 and packet_head[1] == 0x11:  # 状态包数据
            status_packet_data = sock.recv(14)  # 状态包数据
            if status_packet_data[12] == 0xFF and status_packet_data[13] == 0xEE:
                # Radar_frame_length = unpack('B',status_packet_data[5])  # 后续所跟随的track_packet数量
                Radar_frame_length = status_packet_data[5]
                # print("状态包中表明跟踪数量", Radar_frame_length)
                # 获取跟踪包数据
                Radar_frame_list = []  # 用于存放每一帧雷达的数据，存放n个目标,因为每次都初始化一个新的列表，所以是深copy
                current_time = datetime.datetime.now().strftime('%d_%H:%M:%S.%f')  # 该帧时间戳
                Radar_frame_list.append(current_time)

                # 如果该帧数据中没有目标，则将该帧数据填充为0，仍然将该帧数据存入雷达列表中。
                if Radar_frame_length == 0:
                    # 如果该帧数据中没有目标，则将该帧数据填充为0，仍然将该帧数据存入雷达列表中。
                    # print("该帧没有跟踪数据")
                    Radar_frame_list.append(0)
                    Radar_frame_list_copy = deepcopy(Radar_frame_list)
                    if len(Radar_list) == delay_size:  # 判断是否开启采集程序
                        del Radar_list[0]  # 已经满足delay_size大小，删除队列前面的数据，并将最新帧数据放在队尾
                        Radar_list.append(Radar_frame_list_copy)  # 将最新帧数据放在队尾
                    else:
                        Radar_list.append(Radar_frame_list_copy)  # 否则直接往队列中添加该帧数据
                    del Radar_frame_list[:]  # 清除帧列表
                    gc.collect()
                    if len(Radar_list) == delay_size and start_storage_flag.empty():  # 判断队列中帧数是否满足要求
                        start_storage_flag.put(1)  # 开启采集存储程序
                    else:
                        pass
                    continue  # 不进行一下操作，直接再次获取雷达数据
                # Radar_frame_length += 1
                while Radar_frame_length > 0:

                    Radar_frame_length = Radar_frame_length - 1
                    Track_packet_head = sock.recv(2)  # 获取跟踪包head
                    if Track_packet_head[0] == 0x01 and Track_packet_head[1] == 0x21:

                        radar_date = sock.recv(32)
                        if radar_date[30] == 0xFF and radar_date[31] == 0xDE:  # 跟踪包校验
                            # print("得到跟踪一个跟踪目标")
                            radar_date_unpacked = unpack('<HIffffhhBBBccc', radar_date)
                            Track_list = list(radar_date_unpacked)  # 每一个跟踪目标的数据
                            Radar_frame_list.append(Track_list)  # 存储到每帧数据列表中，嵌套list,此处是深copy
                        else:
                            pass
                # print("该帧接收成功")
                Radar_frame_list_copy = deepcopy(Radar_frame_list)
                if len(Radar_list) == delay_size:  # 判断队列是否达到设定帧数大小
                    del Radar_list[0]  # 已经满足delay_size大小，删除队列前面的数据，并将最新帧数据放在队尾
                    Radar_list.append(Radar_frame_list_copy)  # 将最新帧数据放在队尾
                else:
                    Radar_list.append(Radar_frame_list_copy)  # 否则直接往队列中添加该帧数据
                del Radar_frame_list[:]  # 清除帧列表
                gc.collect()
                if len(Radar_list) == delay_size and start_storage_flag.empty():  # 判断队列中帧数是否满足要求
                    start_storage_flag.put(1)  # 开启采集存储程序
                else:
                    pass  # 再次获取雷达数据
                # print("Radar_list：：：：：",Radar_list)
                # print("一帧结束")

        elif packet_head[0] == 0x01 and packet_head[1] == 0x51:  # 来向统计包数据
            statistics_packet_data = sock.recv(46)  # 统计包数据，取了未用
        elif packet_head[0] == 0x01 and packet_head[1] == 0x52:  # 去向统计包数据
            statistics_packet_data = sock.recv(46)  # 统计包数据，取了未用
        elif packet_head[0] == 0x01 and packet_head[1] == 0x54:  # 来向事件包数据
            event_packet_data = sock.recv(22)  # 事件包数据，取了未用
        elif packet_head[0] == 0x01 and packet_head[1] == 0x55:  # 去向事件包数据
            event_packet_data = sock.recv(22)  # 事件包数据，取了未用
        elif packet_head[0] == 0x01 and packet_head[1] == 0x61:  # 来向队列包数据
            quene_packet_data = sock.recv(10)  # 队列包数据，取了未用
        elif packet_head[0] == 0x01 and packet_head[1] == 0x62:  # 去向队列包数据
            quene_packet_data = sock.recv(10)  # 队列包数据，取了未用
        else:
            pass
    print('end *******************************************************************')
    # 发送一些数据到客户端
    # client_socket.send("thank you !".encode('gbk'))
    # 关闭为这个客户端服务的套接字，只要关闭了，就意味着为不能再为这个客户端服务了，如果还需要服务，只能再次重新连接
    sock.close()
