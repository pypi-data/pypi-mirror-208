import time
from vive_tracker_apiserver.client import Client

def get_description(data):
    return str([f'id:{item.meta.uid} x: {item.pos_x:.2f} y: {item.pos_y:.2f} z: {item.pos_z:.2f}' for item in data.payload])

def test_server():
    endpoint = "localhost:8080"

    c = Client(endpoint)
    response = c.get_group()
    print("GetTrackerGroup client received: " + str(response))

    stream = c.open_group_stream()
    print("GetTrackerGroupStream client received: " + str(response))

    try:
        while True:
            data = stream.read()
            if data.meta.valid == False:
                time.sleep(0.05)
                continue
            print('\r'+get_description(data), end="")
    except KeyboardInterrupt as e:
        stream.close()

if __name__ == '__main__':
    test_server()