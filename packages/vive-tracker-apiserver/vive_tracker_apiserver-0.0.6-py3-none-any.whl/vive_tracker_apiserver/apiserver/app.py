import argparse
import logging
import threading
import time
from typing import Optional, Dict, Union, Tuple, Any, List

import numpy as np
from scipy.spatial.transform import Rotation as R

from vive_tracker_apiserver.common import Config
from vive_tracker_apiserver.third_party import triad_openvr


class Application:
    __CONFIG_BUFFER_SIZE__ = 1024
    logger: logging.Logger
    option: Config
    cnt: int
    interval_s: float
    tracker_state_buffer: List[Tuple[dict, dict]]
    thread: Optional[threading.Thread]

    def __init__(self, cfg) -> None:
        if isinstance(cfg, Config):
            self.option = cfg
        elif isinstance(cfg, str):
            self.option = Config(cfg)
        elif isinstance(cfg, argparse.Namespace):
            self.option = Config(cfg.config)
        else:
            raise TypeError(
                "cfg must be Config, str, or argparse.Namespace"
            )
        if self.option.valid is False:
            raise ValueError("invalid config file")

        self.logger = logging.getLogger("apiserver.app")
        self.vr = triad_openvr.triad_openvr()
        self.logger.info('loading openvr components')
        [(time.sleep(1), print(".", end="")) for _ in range(3)]
        print('\n')
        self.logger.info("server is tarted!")

        self.vr_device_mapping = {x.get_serial(): index for index, x in self.vr.devices.items() if x.get_serial() in [x.uid for x in self.option.trackers]}
        self.cnt = np.int(0)
        self.interval_s = 1 / 250
        self.tracker_state_buffer = [
                                        (
                                            dict(
                                                index=-1,
                                                sys_ts_ns=0,
                                                uid="",
                                                valid=False
                                            ),
                                            dict()
                                        )
                                    ] * self.__CONFIG_BUFFER_SIZE__
        self.thread = None

    def start_thread(self):
        def fix_vive_pose_matrix(pose_matrix):
            if pose_matrix is None:
                return None
            else:
                OPENXR_TO_RHS = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])

                pose_matrix = np.array(
                    [
                        list(pose_matrix[0]),
                        list(pose_matrix[1]),
                        list(pose_matrix[2]),
                        [0, 0, 0, 1]
                    ]
                )

                pose_matrix[:3, 3:4] = OPENXR_TO_RHS @ pose_matrix[:3, 3:4]
                # pose_matrix[:3, 3:4] = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]]) @ pose_matrix[:3, 3:4]
                pose_matrix[:3, :3] = OPENXR_TO_RHS @ np.linalg.inv(np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]]) @ pose_matrix[:3, :3])

                return np.concatenate([pose_matrix[:3, 3], R.from_matrix(pose_matrix[:3, :3]).as_quat()])

        def update_vive_tracker_thread(interval_s):
            while True:
                start_t = time.time()
                meta = dict(
                    index=self.cnt,
                    sys_ts_ns=time.time_ns(),
                    uid="",
                    valid=True
                )
                payload = {device_uid: fix_vive_pose_matrix(self.vr.devices[self.vr_device_mapping[device_uid]].get_pose_matrix()) for device_uid in self.vr_device_mapping.keys()}
                meta['sys_ts_ns'] = int((time.time_ns() + meta['sys_ts_ns']) / 2)
                meta['valid'] = all(map(lambda x: x is not None, payload.values()))
                self.tracker_state_buffer[self.cnt % self.__CONFIG_BUFFER_SIZE__] = (
                    meta,
                    payload
                )

                self.cnt += 1
                sleep_t = interval_s - (time.time() - start_t)
                if sleep_t > 0:
                    time.sleep(sleep_t)

        self.thread = threading.Thread(target=update_vive_tracker_thread, args=(self.interval_s,), daemon=True)
        self.thread.start()

    def get_single(self, device_uid: str, index=None) -> Tuple[Dict[str, Any], Optional[List[Union[int, float]]]]:
        index = self.cnt - 1 if index is None else index
        meta, data = self.tracker_state_buffer[index % self.__CONFIG_BUFFER_SIZE__]
        meta['uid'] = device_uid
        return meta, data[device_uid]

    def get_group(self, index=None) -> Tuple[Dict[str, Any], Optional[Dict[str, List[Union[int, float]]]]]:
        index = self.cnt - 1 if index is None else index
        return self.tracker_state_buffer[index % self.__CONFIG_BUFFER_SIZE__]

    def start_recording(self, tag: str) -> Optional[Exception]:
        raise NotImplementedError

    def stop_recording(self) -> Optional[Exception]:
        raise NotImplementedError

    def shutdown(self):
        return None


if __name__ == '__main__':
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="./config.yaml")
    run_args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(level=logging.INFO)

    app = Application(run_args)

    try:
        while True:
            print(app.get_group())

    except KeyboardInterrupt as e:
        app.shutdown()
