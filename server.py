#
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# server.py - the server program for taking request from the client and 
#             send the requested file back to the client
#

import sys
import socket
import threading

def server(server_port):
    serverPort = server_port
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)
    print("Server ready to receive")

    # 接受视频名称，并返回对应的mdp文件。
    connectionSocket, addr = serverSocket.accept()
    video_name = connectionSocket.recv(1024)
    first_part_mpd = './data/'
    third_part_mpd = '/manifest.mpd'
    mpd_addr = first_part_mpd + video_name.decode() + third_part_mpd

    try:
        with open(mpd_addr, "r") as f:
            mdp_file = f.read()
    except FileNotFoundError:
        mdp_file = "video not found"

    connectionSocket.send(mdp_file.encode())

    # 接受视频清晰度，并返回对应的m4s文件。
    index = 0
    while True:
        bandwidth = connectionSocket.recv(1024)

        m4s_addr = './data/' + video_name.decode() + '/chunks/' + video_name.decode() + '_' + bandwidth.decode() + '_' + str(
            index).zfill(5) + '.m4s'
        print("m4s_addr: " + m4s_addr)

        try:
            with open(m4s_addr, "rb") as f:
                m4s_file = f.read()
            for i in range(0, len(m4s_file), 2048):
                chunk1 = m4s_file[i:i + 2048]
                connectionSocket.send(chunk1)
            connectionSocket.send(b"END_OF_FILE")

        except FileNotFoundError:
            m4s_file = b"finished"
            connectionSocket.send(m4s_file)
            break

        index = index + 1

    # 全部完成，终止程序
    serverSocket.close()


if __name__ == '__main__':
    server_port = int(sys.argv[1])
    server(server_port)
