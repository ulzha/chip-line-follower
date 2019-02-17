#!/usr/bin/env python

import socket

from drive import drive, coast, turn_smooth


def command_iter():
    """ Yields control commands that are read from socket, or immediate None if there's no complete command read.
    Commands are newline separated strings.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', 8001))
    server.listen(1)
    print("Listening for a connection on port 8001...")
    (control_socket, address) = server.accept()
    control_socket.setblocking(False)
    command_buffer = [bytearray()]
    while True:
        try:
            data = control_socket.recv(4096)
            if not data:
                break
            for b in data:
                if b == 10:  # '\n'
                    command_buffer.append(bytearray(0))
                else:
                    command_buffer[-1].append(b)
        except BlockingIOError:
            # would block waiting for data
            pass

        if len(command_buffer) > 1:
            yield command_buffer.pop(0).decode()
        else:
            yield None


for cmd in command_iter():
    if cmd == 'drive':
        # let follower run in a separate process so that it's easier to implement emergency stop by means of a signal
        pass
