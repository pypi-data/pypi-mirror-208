import sys
import json
import threading
from abc import ABC, abstractmethod
from typing import List, Callable

import digi
from digi.data import logger, zjson
from digi.data import sync
from digi.data import router
from digi.data import util


class Pool(ABC):
    @abstractmethod
    def __init__(self, name: str):
        self.name = name
        self.lock = threading.Lock()

    @abstractmethod
    def load(self, objects: List[dict]):
        raise NotImplementedError

    @abstractmethod
    def query(self, query: str):
        raise NotImplementedError


class ZedPool(Pool):
    def __init__(self, name):
        super().__init__(name)
        self.client = digi.data.lake

    def load(self, objects: List[dict], *,
             branch="main",
             encoding="zjson",
             same_type=False):
        # update event and processing time
        now = util.now()
        if encoding == "zjson":
            for o in objects:
                # event_ts will be attached at the first
                # data router if does exist from the source
                if "event_ts" not in o:
                    o["event_ts"] = o.get("ts", now)
                o["ts"] = now
            data = "".join(zjson.encode(objects))
        elif encoding == "json":
            zjson_now = zjson.encode_datetime(now)  # as str
            for o in objects:
                if "event_ts" not in o:
                    o["event_ts"] = o.get("ts", zjson_now)
                o["ts"] = zjson_now
            data = "\n".join(json.dumps(o) for o in objects)
        else:
            raise NotImplementedError

        self.lock.acquire()
        try:
            # TBD better source name
            meta = json.dumps({f"{digi.name}": zjson.encode_datetime(now)})
            self.client.load(self.name, data,
                             branch_name=branch,
                             commit_author=digi.name,
                             meta=meta)
            # TBD load from digi also commits source ts in meta
        except Exception as e:
            logger.warning(f"unable to load "
                           f"{data} to {self.name}: {e}")
        finally:
            self.lock.release()

    def query(self, query: str):
        if query != "":
            query = f"| {query}"
        query = f"from {self.name} {query}"
        return self.client.query(query)

    def watch(self, fn: Callable,
              branch: str = "main",
              *,
              in_flow: str = "",
              eoio: bool = True,
              ):
        """Watch changes of the main pool and run UDF."""
        source = f"{self.name}@{branch}"
        return sync.Watch(fn,
                          sources=[source],
                          eoio=eoio,
                          in_flow=in_flow)

    def create_branch_if_not_exist(self, branch: str):
        if not self.client.branch_exist(self.name, branch):
            self.client.create_branch(self.name, branch)
            self.load([router.Egress.INIT], branch=branch)
            logger.info(f"load {router.Egress.INIT} to {self.name}@{branch}")


def pool_name(g, v, r, n, ns):
    _, _, _ = g, v, r
    if ns == "default":
        return f"{n}"
    else:
        # TBD update digi creation
        return f"{ns}_{n}"


providers = {
    "zed": ZedPool
    # ...
}


def create_pool():
    global providers
    if digi.lake_provider == "":
        digi.lake_provider = "zed"

    if digi.lake_provider in {"none", "false"}:
        return None

    if digi.lake_provider not in providers:
        logger.fatal(f"unknown lake provider {digi.lake_provider}")
        sys.exit(1)

    return providers[digi.lake_provider](
        pool_name(*digi.duri)
    )
