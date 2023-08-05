# Vive Tracker APIServer

## Get Started

```shell
pip install vive-tracker-apiserver
```

From source:

```shell
git clone https://github.com/mvig-robotflow/vive-tracker-apiserver
cd vive-tracker-apiserver
python setup.py install
```

## Usage

### Set up the SteamVR

First, install [SteamVR](https://www.steamvr.com/zh-cn/). Configure and pair the trackers with HMD or receiver.

Then run the configuration command:

```shell
python -m vive_tracker_apiserver configure
```

This will automatically detect all trackable devices and generate a `config.yaml` file under `$pwd`. It looks like [this](manifests/config.yaml)

```yaml
vive_tracker_apiserver:
  api:
    interface: 0.0.0.0
    port: 8080
  data_path: ./tracker_data
  debug: false
  trackers:
  - name: tracker_1
    uid: LHR-656F5409
  - name: tracker_2
    uid: LHR-6A736404
```

> The screen might blink during this configuration

After the configuration. Run the apiserver with configuration

```shell
python -m vive_tracker_apiserver serve --config=config.yaml
```

```text
...
INFO:apiserver.app:loading openvr components
...
INFO:apiserver.app:server is tarted!
INFO:apiserver.app:vive tracker service listen at 8080
INFO:apiserver.app:vive tracker config Config(path='./config.yaml', trackers=[TrackerConfig(uid='LHR-656F5409', name='tracker_1'), TrackerConfig(uid='LHR-6A736404', name='tracker_2')], api_port=8080, api_interface='0.0.0.0', debug=False, data_path='./tracker_data', valid=True)
```

Here is a minimal working example:

```python
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
```

## gRPC Server

Run this command

```shell
python -m vive_tracker_apiserver serve
```

### Testing with cli tools

```shell
python -m vive_tracker_apiserver test.server
```

You will be asked to input API endpoint.

### Testing with Open3D visualization

```shell
python -m vive_tracker_apiserver test.visualize
```

You will be asked to input API endpoint.

### Generate Client

First run `cd vive_tracker_apiserver/grpc`, then run:

```shell
# cd vive_tracker_apiserver/grpc
python -m grpc_tools.protoc -I../../manifests/protos --python_out=. --pyi_out=. --grpc_python_out=. ../../manifests/protos/tracker_packet.proto
```

You might need to replace line 5 of `vive_tracker_apiserver/grpc/tracker_packet_pb2_grpc.py` with `import vive_tracker_apiserver.grpc.tracker_packet_pb2 as tracker__packet__pb2`


