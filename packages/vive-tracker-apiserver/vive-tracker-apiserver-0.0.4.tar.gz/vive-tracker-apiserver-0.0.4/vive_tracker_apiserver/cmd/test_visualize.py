import logging
import os
import time

import numpy as np
import open3d as o3d
import transforms3d as t3d
from py_cli_interaction import must_parse_cli_string

from vive_tracker_apiserver.client import Client


def get_live_visualizer():
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    return vis


def test_visualize():
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
    endpoint = must_parse_cli_string("endpoint", "localhost:8080")

    c = Client(endpoint)
    response = c.get_group()
    base = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=np.array([0., 0., 0.]))
    tracker_meshes = {
        x.meta.uid: o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2, origin=np.array([0., 0., 0.])) for x in response.payload
    }
    tracker_transforms = {
        x.meta.uid: np.eye(4) for x in response.payload
    }
    vis = get_live_visualizer()
    [vis.add_geometry(source) for _, source in tracker_meshes.items()]
    vis.add_geometry(base)

    try:
        while True:
            data = c.get_group()
            if data.meta.valid == False:
                time.sleep(0.0005)
                continue

            for x in data.payload:
                T = np.eye(4)
                T[:3, :3] = t3d.quaternions.quat2mat([x.rot_w, x.rot_x, x.rot_y, x.rot_z])
                T[:3, 3] = [x.pos_x, x.pos_y, x.pos_z]
                T_diff = T @ np.linalg.inv(tracker_transforms[x.meta.uid])
                tracker_transforms[x.meta.uid] = T_diff @ tracker_transforms[x.meta.uid]

                tracker_meshes[x.meta.uid].transform(T_diff)
                vis.update_geometry(tracker_meshes[x.meta.uid])
            if not vis.poll_events():
                break
            vis.update_renderer()
    except KeyboardInterrupt as e:
        logging.info("got KeyboardInterrupt")

    finally:
        vis.destroy_window()
        vis.close()
        os._exit(0)


if __name__ == '__main__':
    test_visualize()
