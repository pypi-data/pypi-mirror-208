import pickle
import socket
import tenacity
import dill


def serve(data, port=54545):
    """Broadcast the data."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', port))
        while True:
            buff, address = s.recvfrom(1024)
            if buff == b'Hello':
                s.sendto(str(data).encode(), address)


@tenacity.retry(wait=tenacity.wait_fixed(1),
                stop=tenacity.stop_after_attempt(5))
def find_data_source(port=54545):
    """Find the data source."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', 0))
        s.sendto(b'Hello', ('<broadcast>', port))
        s.settimeout(1)
        data, addr = s.recvfrom(1024)
        return addr[0], int(data.decode())


def get_data_from_source(source):
    """Get data from the source."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(source)
        data = b''
        while True:
            packet = s.recv(1024)
            if not packet:
                break
            data += packet
        return dill.dumps(data)
