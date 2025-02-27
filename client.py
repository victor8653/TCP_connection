# 
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# client.py - the client program for sending request to the server and play the received video chunks
#

import threading
from queue import Queue
from video_player import play_chunks
import sys
import socket
import re
import time
import os

def client(server_addr, server_port, video_name, alpha, chunks_queue):
    """
    the client function
    write your code here

    arguments:
    server_addr -- the address of the server
    server_port -- the port number of the server
    video_name -- the name of the video
    alpha -- the alpha value for exponentially-weighted moving average
    chunks_queue -- the queue for passing the path of the chunks to the video player
    """

    # to visualize the adaptive video streaming, store the chunk in a temporary folder and
    # pass the path of the chunk to the video player
    # 
    # # create temporary directory if not exist
    # if not os.path.exists("tmp"):
    #     os.makedirs("tmp")
    # # write chunk to the temporary directory
    # with open(f"tmp/chunk_0.m4s", "wb") as f:
    #     f.write(chunk)
    # # put the path of the chunk to the queue
    # chunks_queue.put(f"tmp/chunk_0.m4s")

    serverName = server_addr
    serverPort = server_port
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    message1 = video_name
    clientSocket.send(message1.encode())
    mdp_file = clientSocket.recv(2048)

    if mdp_file.decode() == "video not found":
        sys.exit()

    bandwidths = re.findall(r'bandwidth="(\d+)"', mdp_file.decode())
    sorted_bandwidths_int = sorted(map(int, bandwidths))
    bandwidths = list(map(str, sorted_bandwidths_int))

    zero_time = time.time()
    index = 0
    band_i = 0
    T_current = 0
    f_txt = open("log.txt", "w")

    while True:
        start_time = time.time()
        clientSocket.send(bandwidths[band_i].encode())

        received_chunk = b""
        while True:
            part_chunk = clientSocket.recv(2048)

            if part_chunk == b"finished":
                break

            received_chunk += part_chunk

            if received_chunk.endswith(b'END_OF_FILE'):
                break

        end_time = time.time()

        # 选取下一个速率
        bit_size = len(received_chunk) * 8
        time_difference = end_time - start_time
        T_new = bit_size / time_difference
        T_current = (1-alpha) * T_current + alpha * T_new
        band_i = max((i for i, x in enumerate(sorted_bandwidths_int) if x < T_current), default=None)

        if part_chunk == b"finished":
            break

        

        save_path = "./tmp/chunk_{" + str(index) + "}.m4s"
        #save_path = f"./tmp/chunk_{index}.m4s"

        if not os.path.exists("tmp"):
            os.makedirs("tmp")


        with open(save_path, "wb") as f:
            f.write(received_chunk)

        chunks_queue.put(save_path)
        print(save_path)

        s1 = f"{start_time - zero_time} {time_difference} {T_new} {T_current} {bandwidths[band_i]} bunny-{bandwidths[band_i]}-{str(index).zfill(5)}.m4s \n "
        f_txt.write(s1)

        index = index + 1

    clientSocket.close()
    f_txt.close()
    print(f"empty: {chunks_queue.empty()}")


# parse input arguments and pass to the client function
if __name__ == '__main__':
    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])
    video_name = sys.argv[3]
    alpha = float(sys.argv[4])

    # init queue for passing the path of the chunks to the video player
    chunks_queue = Queue()
    # start the client thread with the input arguments
    client_thread = threading.Thread(target=client, args=(server_addr, server_port, video_name, alpha, chunks_queue))
    client_thread.start()
    print("hello")
    #time.sleep(5)
    print("hello2")
    print(f"out: empty?{chunks_queue.empty()}")
    # start the video player
    play_chunks(chunks_queue)
