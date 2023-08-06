import redis
from json import dumps, loads
import requests
from typing import Any, List, Union, ForwardRef, Callable, Tuple
from enum import Enum
from typing_utils import get_origin
from datetime import datetime
from dataclasses import _FIELDS  # type:ignore
from uuid import uuid1
DATETIME_FORMAT = "%Y-%m-%dZ%H:%M:%S.%f"


class Cache(object):
    def __init__(self, config):
        self.redis = redis.Redis(host=config["host"], port=config["port"], db=0)
        self.ttl = config["ttl"]
        self.prefix = config["prefix"] + ":"

    def __contains__(self, key):
        return self.redis.exists(self.prefix + str(key))

    def __getitem__(self, key):
        val = self.redis.get(self.prefix + str(key))
        if val is None:
            raise ValueError("Cache Key Not Found", key)
        return loads(val)

    def __setitem__(self, key, value):
        self.redis.set(self.prefix + str(key), dumps(value), ex=self.ttl)

    def __delitem__(self, key):
        return self.redis.delete(self.prefix + str(key))

    def clear(self):
        return self.redis.flushall()


class Module:
    def __init__(self, config):
        self.name = config["name"]
        if "cache" in config:
            self.cache = Cache(config["cache"])
        self.use_cache = "cache" in config
        self.address = f"http://{config['host']}:{config['port']}/"
        self.config = config

    def post(self, endpoint, *args):
        try:
            resp = requests.post(self.address + endpoint, json={"__args__": args})
            return resp.json()["data"]
        except Exception as e:
            print(f"ERROR: {self.name}", args, flush=True)
            print(e, flush=True)


def _fill(cls, dict, key, default, builder=None):
    try:
        val = dict.get(key, default)
        if val is not None:
            if builder is not None:
                val = builder(val, cls)
        dict[key] = val
    except Exception as e:
        print("FILL Error:", key, dict, default)
        raise e


class Dictable:
    filler_args: List

    @staticmethod
    def decorator(cls_def):
        def type_matcher(type) -> Tuple[Any, Callable]:
            if get_origin(type) == list:
                _, builder = type_matcher(type.__args__[0])
                return [], lambda vs, cls: [builder(v, cls) for v in vs]
            elif get_origin(type) == dict:
                _, builder = type_matcher(type.__args__[1])
                return {}, lambda d, cls: {k: builder(v, cls) for k, v in d.items()}
            elif get_origin(type) == Union:
                _, builder = type_matcher(type.__args__[1])
                return None, lambda v, cls: builder(v, cls)
            elif get_origin(type) == tuple:
                return (), lambda v, cls: v
            elif type == Any:
                return None, lambda v, cls: v
            elif isinstance(type, ForwardRef):
                return None, lambda x, cls: cls.from_dict(x)
            elif issubclass(type, Enum):
                return "", lambda v, cls: type(v)
            elif issubclass(type, Dictable):
                return {}, lambda v, cls: type.from_dict(v)
            elif type == datetime:
                return (
                    datetime.strftime(datetime.now(), DATETIME_FORMAT),
                    lambda txt, cls: datetime.strptime(txt, DATETIME_FORMAT),
                )
            else:
                return None, lambda x, cls: x

        cls_def.filler_args = []
        attributes = getattr(cls_def.__mro__[0], _FIELDS, None)
        if attributes is None:
            raise ValueError
        for name, attribute in attributes.items():
            default, builder = type_matcher(attribute.type)
            cls_def.filler_args.append((name, default, builder))

        cls_def.__hash__ = Dictable.__hash__
        return cls_def

    def to_dict(self):
        def type_matcher(v):
            if isinstance(v, Dictable):
                return v.to_dict()
            elif isinstance(v, list):
                return [type_matcher(v_) for v_ in v]
            elif isinstance(v, dict):
                return {k: type_matcher(v_) for k, v_ in v.items()}
            elif isinstance(v, datetime):
                return datetime.strftime(v, DATETIME_FORMAT)
            elif isinstance(v, Enum):
                return v.value
            else:
                return v

        return {k: type_matcher(v) for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, dictionary):
        for name, default, builder in cls.filler_args:
            _fill(cls, dictionary, name, default, builder)
        return cls(**dictionary)

    def __hash__(self) -> int:
        return hash(dumps(self.to_dict(), sort_keys=True))

    def __eq__(self, other) -> bool:
        if isinstance(other, Dictable):
            return hash(self) == hash(other)
        else:
            return False

    @staticmethod
    def new_id():
        return str(uuid1())
