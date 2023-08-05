from typing import Any

import grpc

import vive_tracker_apiserver.grpc.tracker_packet_pb2 as pb2
import vive_tracker_apiserver.grpc.tracker_packet_pb2_grpc as pb2_grpc


class ClientStream:
    response: Any = None

    def __init__(self, response: Any):
        self.response = response

    def read(self):
        return next(self.response)

    def close(self):
        self.response.cancel()


class Client:
    endpoint: str
    channel: grpc.Channel = None
    stub: pb2_grpc.TrackerServiceStub = None

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
        self.channel = grpc.insecure_channel(self.endpoint)
        self.stub = pb2_grpc.TrackerServiceStub(self.channel)

    def reconnect(self):
        if self.channel is not None:
            self.channel.close()
        self.channel = grpc.insecure_channel(self.endpoint)
        self.stub = pb2_grpc.TrackerServiceStub(self.channel)

    def get_group(self):
        return self.stub.GetTrackerGroup(
            pb2.TrackerRequest(uid="")
        )

    def open_group_stream(self):
        return ClientStream(
            self.stub.GetTrackerGroupStream(
                pb2.TrackerRequest(uid="")
            )
        )


def get_client(endpoint: str) -> Client:
    return Client(endpoint)
