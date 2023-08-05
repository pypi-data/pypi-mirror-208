import time

import tqdm
from py_cli_interaction import must_parse_cli_string

from vive_tracker_apiserver.client import Client


def get_description(data):
    return str([f'id:{item.meta.uid} x: {item.pos_x:.2f} y: {item.pos_y:.2f} z: {item.pos_z:.2f}' for item in data.payload])


def test_server():
    endpoint = must_parse_cli_string("endpoint", "localhost:8080")

    c = Client(endpoint)
    response = c.get_group()
    print("GetTrackerGroup client received: " + str(response))

    stream = c.open_group_stream()
    print("GetTrackerGroupStream client received: " + str(response))

    try:
        with tqdm.tqdm() as pbar:
            while True:
                data = stream.read()
                if data.meta.valid == False:
                    time.sleep(0.05)
                    continue
                pbar.set_description(get_description(data))
                pbar.update(1)
                # time.sleep(0.05)
                # print)
    except KeyboardInterrupt as e:
        stream.close()


if __name__ == '__main__':
    test_server()
