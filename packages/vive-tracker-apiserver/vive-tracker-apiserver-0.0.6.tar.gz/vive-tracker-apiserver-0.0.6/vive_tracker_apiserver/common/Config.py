from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

import yaml


@dataclass
class TrackerConfig:
    uid: str
    name: str = field(default='')


@dataclass
class Config:
    path: str = field(default='')
    trackers: List[TrackerConfig] = field(default_factory=list)
    api_port: int = field(default=8080)
    api_interface: str = field(default='0.0.0.0')
    debug: bool = field(default=False)
    data_path: str = field(default='./tracker_data', init=False)
    valid: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        err = self.load()
        if err is None:
            self.valid = True
        else:
            self.valid = False

    def from_dict(self, cfg: Dict[str, Any]):
        self.trackers = [TrackerConfig(**s) for s in cfg['trackers']]
        if 'api' in cfg.keys():
            self.api_port = cfg['api']['port'] if 'port' in cfg['api'] else self.api_port
            self.api_interface = cfg['api']['interface'] if 'interface' in cfg['api'] else self.api_interface
        self.debug = cfg['debug'] if 'debug' in cfg.keys() else self.debug
        self.data_path = cfg['data_path'] if 'data_path' in cfg else self.data_path
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trackers": [
                {
                    "uid": s.uid,
                    'name': s.name
                }
                for s in self.trackers
            ],
            "api": {
                "port": self.api_port,
                "interface": self.api_interface
            },
            "data_path": self.data_path,
            "debug": self.debug
        }

    def load(self) -> Optional[Exception]:
        if self.path is not None:
            try:
                cfg_dict = yaml.load(open(self.path, "r"),
                                     Loader=yaml.SafeLoader)
            except Exception as e:
                return e

            try:
                self.from_dict(cfg_dict['vive_tracker_apiserver'])
                return None

            except Exception as e:
                return e

        else:
            return Exception("Config path is not set")

    def dump(self) -> Optional[Exception]:
        if self.path is not None:
            try:
                with open(self.path, 'w') as f:
                    yaml.dump(self.to_dict(), f)
                    return None
            except Exception as e:
                return Exception("Failed to dump config")
        else:
            return Exception("Config path is not set")
