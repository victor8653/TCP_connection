#
# Columbia University - CSEE 4119 Computer Networks
# Assignment 1 - Adaptive video streaming
#
# server.py - the server program for taking requests from the client and 
#             sending the requested file back to the client
#

import sys
import socket
import threading


def server(server_port):
    """
    The server function that listens for client requests, sends the manifest file, 
    and transmits requested video chunks.

    Arguments:
    server_port -- The port number the server listens on.
    """

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", server_port))
    server_socket.listen(1)
    print("Server ready to receive")

    # Accept a connection from the client
    connection_socket, addr = server_socket.accept()

    # Receive the requested video name and send the corresponding MPD file
    video_name = connection_socket.recv(1024)
    mpd_addr = f'./data/{video_name.decode()}/manifest.mpd'

    try:
        with open(mpd_addr, "r") as f:
            mpd_file = f.read()
    except FileNotFoundError:
        mpd_file = "video not found"

    connection_socket.send(mpd_file.encode())

    # Receive the requested bitrate and send the corresponding m4s file
    index = 0
    while True:
        bandwidth = connection_socket.recv(1024)

        m4s_addr = f'./data/{video_name.decode()}/chunks/{video_name.decode()}_' \
                   f'{bandwidth.decode()}_{str(index).zfill(5)}.m4s'
        print(f"m4s_addr: {m4s_addr}")

        try:
            with open(m4s_addr, "rb") as f:
                m4s_file = f.read()
            for i in range(0, len(m4s_file), 2048):
                chunk = m4s_file[i:i + 2048]
                connection_socket.send(chunk)
            connection_socket.send(b"END_OF_FILE")

        except FileNotFoundError:
            connection_socket.send(b"finished")
            break

        index += 1

    # Close the server socket after sending all chunks
    server_socket.close()


if __name__ == '__main__':
    """
    The main function that parses the command-line argument for the server port 
    and starts the server.
    """

    server_port = int(sys.argv[1])
    server(server_port)
