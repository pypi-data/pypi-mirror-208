import logging
from concurrent import futures
from typing import List, Dict, Any
import time

import grpc

import vive_tracker_apiserver.grpc.tracker_packet_pb2 as pb2
import vive_tracker_apiserver.grpc.tracker_packet_pb2_grpc as pb2_grpc
from vive_tracker_apiserver.apiserver.app import Application
from vive_tracker_apiserver.common.Config import Config

logger = logging.getLogger("apiserver.server")


def create_tracker_single_packet(meta: Dict[str, Any], pos_quat_7d: List[float] = None, uid: str = None):
    if uid is not None:
        meta['uid'] = uid
    if pos_quat_7d is None:
        meta['valid'] = False
        return pb2.TrackerSingleResponse(meta=pb2.TrackerMetaResponse(**meta))
    else:
        meta['valid'] = True
        return pb2.TrackerSingleResponse(meta=pb2.TrackerMetaResponse(**meta),
                                         pos_x=pos_quat_7d[0],
                                         pos_y=pos_quat_7d[1],
                                         pos_z=pos_quat_7d[2],
                                         rot_w=pos_quat_7d[3],
                                         rot_x=pos_quat_7d[4],
                                         rot_y=pos_quat_7d[5],
                                         rot_z=pos_quat_7d[6])


def create_tracker_group_packet(meta: Dict[str, Any], payload: Dict[str, List[float]]):
    if any([x is None for x in payload.values()]):
        meta['valid'] = False
    else:
        meta['valid'] = True

    return pb2.TrackerGroupResponse(meta=pb2.TrackerMetaResponse(**meta),
                                    payload=[
                                        create_tracker_single_packet(meta=meta, pos_quat_7d=v, uid=k) for k, v in payload.items()
                                    ])


class TrackerService(pb2_grpc.TrackerService):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.app: Application = Application(config)
        self.app.start_thread()
        self.app.logger.info(f"vive tracker service listen at {config.api_port}")
        self.app.logger.info(f"vive tracker config {config}")

    def GetTrackerGroup(self,
                        target,
                        options=(),
                        channel_credentials=None,
                        call_credentials=None,
                        insecure=False,
                        compression=None,
                        wait_for_ready=None,
                        timeout=None,
                        metadata=None):
        logger.debug(f"GetTrackerGroup: {target}")
        meta, payload = self.app.get_group()
        return create_tracker_group_packet(meta, payload)

    def GetTrackerGroupStream(self,
                              target,
                              options=(),
                              channel_credentials=None,
                              call_credentials=None,
                              insecure=False,
                              compression=None,
                              wait_for_ready=None,
                              timeout=None,
                              metadata=None):
        logger.info(f"GetTrackerGroupStream: {target}")
        options.add_callback(lambda: logger.info(
            "GetTrackerGroupStream: context deadline exceeded"))

        meta, payload = self.app.get_group()
        last_index = meta['index']
        yield create_tracker_group_packet(meta, payload)

        while True:
            start_t = time.time()
            desired_index = last_index + 1
            meta, payload = self.app.get_group(index=desired_index)

            if not meta['valid'] or meta['index'] < desired_index:
                sleep_t = self.app.interval_s - (time.time() - start_t)
                if sleep_t > 0:
                    time.sleep(sleep_t)
                continue

            else:
                if meta['index'] > desired_index:
                    logger.warning('slow client operation detected')
                last_index = meta['index']
                yield create_tracker_group_packet(meta, payload)

    def GetTrackerSingle(self,
                         target,
                         options=(),
                         channel_credentials=None,
                         call_credentials=None,
                         insecure=False,
                         compression=None,
                         wait_for_ready=None,
                         timeout=None,
                         metadata=None):
        logger.debug(f"GetTrackerSingle: {target}")
        meta, payload = self.app.get_single(target.addr)
        return create_tracker_single_packet(meta, payload)

    def GetTrackerSingleStream(self,
                               target,
                               options=(),
                               channel_credentials=None,
                               call_credentials=None,
                               insecure=False,
                               compression=None,
                               wait_for_ready=None,
                               timeout=None,
                               metadata=None):
        logger.info(f"GetTrackerSingleStream: {target}")
        options.add_callback(lambda: logger.info(
            "GetTrackerGroupStream: context deadline exceeded"))

        meta, payload = self.app.get_single(target.uid)
        last_index = meta['index']
        yield create_tracker_single_packet(meta, payload)

        while True:
            start_t = time.time()
            desired_index = last_index + 1
            meta, payload = self.app.get_single(target.uid, index=desired_index)
            if not meta['valid'] or meta['index'] < desired_index:
                sleep_t = self.app.interval_s - (time.time() - start_t)
                if sleep_t > 0:
                    time.sleep(sleep_t)
                continue

            else:
                if meta['index'] > desired_index:
                    logger.warning('slow client operation detected')
                last_index = meta['index']
                yield create_tracker_single_packet(meta, payload)

    # def GetFIFOStatus(self, request: pb2.ForceGetFIFOStatusRequest, context):
    #     return pb2.ForceStatusResponse(status=self.app.fifo_status)
    #
    # def SetFIFOStatus(self, request: pb2.ForceSetFIFOStatusRequest, context):
    #     logger.info(f"SetFIFOStatus: {request}")
    #     if request.status:
    #         err = self.app.start_fifo()
    #     else:
    #         err = self.app.stop_fifo()
    #     return pb2.ForceStatusResponse(status=True, err=str(err))
    #
    # def GetPacket(self, request: pb2.ForcePacketRequest, context):
    #     logger.info(f"GetForcePacket: {request}")
    #     data = self.app.get()
    #     return create_packet(data)
    #
    # def GetPacketStream(self, request: pb2.ForcePacketRequest, context):
    #     logger.info(f"GetForcePacketStream: {request}")
    #     context.add_callback(lambda: logger.info(
    #         "GetPacketStream: context deadline exceeded"))
    #     while True:
    #         data = self.app.get()
    #         # print(data)
    #         yield create_packet(data)
    #
    # def ResetPacketCache(self, request: pb2.ForcePacketRequest, context):
    #     logger.info(f"ResetForcePacketCache: {request}")
    #     self.app.force_data_queue.queue.clear()
    #     return pb2.ForceStatusResponse(status=True, err=str(None))
    #
    # def ToggleRecording(self, request: pb2.ForceToggleRecordingRequest, context):
    #     logger.info(f"ToggleRecording: {request}")
    #     if request.start:
    #         err = self.app.start_recording(request.tag)
    #     else:
    #         err = self.app.stop_recording()
    #     return pb2.ForceStatusResponse(status=True, err=str(err))


def get_server(cfg: Config):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_TrackerServiceServicer_to_server(
        TrackerService(cfg), server)
    server.add_insecure_port(f'{cfg.api_interface}:{cfg.api_port}')
    return server


if __name__ == '__main__':
    server = get_server(Config('./config.yaml'))
    server.start()
    logging.basicConfig(level=logging.INFO)

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
