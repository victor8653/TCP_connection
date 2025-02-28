# 
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# client.py - the client program for sending requests to the server and play the received video chunks
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
    The client function that connects to the server, requests video chunks, 
    and passes them to the video player.

    Arguments:
    server_addr -- The IP address of the server.
    server_port -- The port number of the server.
    video_name -- The name of the requested video.
    alpha -- The alpha value for exponentially-weighted moving average.
    chunks_queue -- A queue for passing chunk file paths to the video player.
    """

    server_name = server_addr
    server_port = server_port
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_name, server_port))

    message1 = video_name
    client_socket.send(message1.encode())
    mdp_file = client_socket.recv(2048)

    if mdp_file.decode() == "video not found":
        sys.exit()

    bandwidths = re.findall(r'bandwidth="(\d+)"', mdp_file.decode())
    sorted_bandwidths_int = sorted(map(int, bandwidths))
    bandwidths = list(map(str, sorted_bandwidths_int))

    zero_time = time.time()
    index = 0
    band_i = 0
    t_current = 0
    f_txt = open("log.txt", "w")

    while True:
        start_time = time.time()
        client_socket.send(bandwidths[band_i].encode())

        received_chunk = b""
        while True:
            part_chunk = client_socket.recv(2048)

            if part_chunk == b"finished":
                break

            received_chunk += part_chunk

            if received_chunk.endswith(b'END_OF_FILE'):
                break

        end_time = time.time()

        # Select the next bitrate
        bit_size = len(received_chunk) * 8
        time_difference = end_time - start_time
        t_new = bit_size / time_difference
        t_current = (1 - alpha) * t_current + alpha * t_new
        band_i = max((i for i, x in enumerate(sorted_bandwidths_int) if x < t_current), default=0)
    


        if part_chunk == b"finished":
            break

        save_path = f"./tmp/chunk_{index}.m4s"

        if not os.path.exists("tmp"):
            os.makedirs("tmp")

        with open(save_path, "wb") as f:
            f.write(received_chunk)

        chunks_queue.put(save_path)
        print(save_path)

        s1 = (f"{start_time - zero_time} {time_difference} {t_new} {t_current} "
              f"{bandwidths[band_i]} bunny-{bandwidths[band_i]}-{str(index).zfill(5)}.m4s \n ")
        f_txt.write(s1)

        index += 1

    client_socket.close()
    f_txt.close()


# Parse input arguments and pass to the client function
if __name__ == '__main__':
    """
    The main function that parses command-line arguments, initializes the chunk queue, 
    and starts the client thread to fetch video chunks.
    """

    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])
    video_name = sys.argv[3]
    alpha = float(sys.argv[4])

    # Initialize queue for passing the path of the chunks to the video player
    chunks_queue = Queue()

    # Start the client thread with the input arguments
    client_thread = threading.Thread(target=client, args=(server_addr, server_port, video_name, alpha, chunks_queue))
    client_thread.start()


    # Start the video player
    play_chunks(chunks_queue)
