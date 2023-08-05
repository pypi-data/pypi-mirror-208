import pprint

import yaml
from py_cli_interaction import must_parse_cli_int, must_parse_cli_bool, must_parse_cli_string

from vive_tracker_apiserver.common import Config, TrackerConfig
from vive_tracker_apiserver.third_party import triad_openvr as triad_openvr


def main(args):
    try:
        v = triad_openvr.triad_openvr()
        while True:
            cfg = Config()

            cfg.api_port = must_parse_cli_int("Enter a port number", 1024, 65535, 8080)
            cfg.api_interface = must_parse_cli_string("Enter a interface", "0.0.0.0")
            cfg.debug = must_parse_cli_bool("Debug mode", False)
            cfg.trackers = [TrackerConfig(uid=x.get_serial(), name=name) for name, x in v.devices.items()]

            res = cfg.to_dict()
            print("Your configuration is:")
            pprint.pprint(res)
            confirm = must_parse_cli_bool("Confirm?", True)

            if confirm:
                break
            else:
                continue

        dest = must_parse_cli_string("Enter save destination", "./config.yaml")
        with open(dest, 'w') as f:
            yaml.dump({'vive_tracker_apiserver': res}, f)
    except KeyboardInterrupt as e:
        print("Exiting...")

    except EOFError as e:
        print("Exiting...")

def entry_point(argv):
    main(None)


if __name__ == '__main__':
    import sys

    main(sys.argv)
