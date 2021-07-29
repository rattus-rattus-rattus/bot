"""
Automatically load certain plugins after bot initialization.
"""

import asyncio
import logging
from typing import List, Set, Tuple, Optional, Iterator, Awaitable, Protocol, cast
import util.asyncio
import util.db.kv
import plugins

class AutoloadConf(Protocol, Awaitable[None]):
    autoload: Optional[List[str]]
    def __getitem__(self, key: str) -> Optional[bool]: ...
    def __setitem__(self, key: str, val: Optional[bool]) -> None: ...
    def __iter__(self) -> Iterator[Tuple[str]]: ...

logger: logging.Logger = logging.getLogger(__name__)
conf: AutoloadConf

@plugins.init_async
async def init() -> None:
    global conf
    conf = cast(AutoloadConf, await util.db.kv.Config.load(__name__))

    if conf.autoload is not None:
        for plugin in conf.autoload:
            conf[plugin] = True
        conf.autoload = None
    await conf

    async def autoload() -> None:
        for name, in conf:
            try:
                # Sidestep plugin dependency tracking
                await plugins.load(name)
            except:
                logger.critical("Exception during autoload of {}".format(name), exc_info=True)
    asyncio.create_task(autoload())

def get_autoload() -> Set[str]:
    return {plugin for plugin, in conf}

def set_autoload(plugin: str, status: bool) -> None:
    conf[plugin] = status or None
