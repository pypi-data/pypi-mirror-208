import argparse
import logging
import time

from vive_tracker_apiserver.apiserver.server import get_server
from vive_tracker_apiserver.common import Config


def main(args):
    logging.basicConfig(level=logging.INFO)
    cfg = Config(args.config)
    if cfg.valid is False:
        logging.error("invalid config file")
        exit(1)

    server = get_server(cfg)
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


def entry_point(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="./config.yaml")
    run_args = parser.parse_args(argv[1:])
    main(run_args)


if __name__ == '__main__':
    import sys

    exit(entry_point(sys.argv))
