from typing import List, Optional
from utils import proxy_tools
from utils import database
import datetime


class ProxyPlugin(object):
    interval = 1 * 60  # 插件的2次抓取等待间隔（秒）

    def get_proxy(self) -> Optional[List[database.Proxy]]:
        yield None
