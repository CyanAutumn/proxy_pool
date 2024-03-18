import datetime
from typing import Dict
from utils import database
from utils import flogger
from utils.web_request import webRequest

log = flogger.Flogger().get_logger(__name__)


def convert_dict_to_proxy(proxy: Dict):
    _ = database.Proxy(
        ip=proxy.get("ip"),
        port=proxy.get("port"),
        location=proxy.get("location"),
        type=proxy.get("type"),
    )
    return _


def convert_proxy_to_dict(proxy: database.Proxy):

    _ = {
        "ip": proxy.ip,
        "port": proxy.port,
        "location": proxy.location,
        "type": proxy.type,
    }
    return _


def check_proxy(proxy: database.Proxy):
    t_proxy = f"{proxy.ip}:{proxy.port}"
    proxies = {}
    type = proxy.type.split(",")
    if "HTTP" in type:
        proxies["http"] = f"http://{t_proxy}"
        proxies["https"] = f"http://{t_proxy}"
    if "HTTPS" in type:
        proxies["https"] = f"https://{t_proxy}"

    response = webRequest().get(
        url="https://searchplugin.csdn.net/api/v1/ip/get?ip=",
        # url="https://www.baidu.com/",
        proxies=proxies,
        retry_interval=1,
        retry_time=2,
    )
    if response is None:
        log.info(f"代理无效 {t_proxy}")
        return False

    log.info(f"代理 {t_proxy} 测试通过 {response.json}")
    return True
