from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from utils import proxy_plugin_base
from utils import proxy_tools
from utils import flogger
from utils import database
import os
import datetime


log = flogger.Flogger().get_logger(__name__)
apscheduler = BackgroundScheduler()
plugin_list = []
proxy_list: List[database.Proxy] = []


def task_check_thread():
    """运行代理检查进程，因为检查地址是同一个网站，所以不能使用并发对网站造成压力"""

    if len(proxy_list) > 0:
        proxy = proxy_list.pop(0)  # 取出
        if proxy_tools.check_proxy(proxy):  # 检查
            proxy.check_date = datetime.datetime.now()
            proxy.create_date = datetime.datetime.now()
            proxy.is_checking = False
            log.info(f"{proxy.ip}:{proxy.port} 有效，进行入库")
            database.check_passed(proxy)  # 入库
        elif database.check_ip_in(proxy):
            database.delete_proxy(proxy)  # 检查失败，删除


def task_crawler_proxy(plugin: proxy_plugin_base.ProxyPlugin):
    """爬虫任务"""
    try:
        t_proxy_list = next(plugin.get_proxy())
        if t_proxy_list is not None:
            for proxy in t_proxy_list:
                if not database.check_ip_in(proxy):
                    proxy_list.append(proxy)
    except Exception as e:
        log.error(f"代理获取插件出现问题 {str(e)}")


def task_check_local_proxy():
    """将本地过期ip放到检查队列最前面"""
    ip_list = database.get_expired_ip_list()
    if ip_list is not None and len(ip_list) > 0:
        proxy_list[:0] = ip_list


def run():
    for filename in os.listdir("./plugin/"):
        if not filename.endswith(".py"):
            continue
        plugin_name = os.path.splitext(filename)[0]
        plugin: proxy_plugin_base = __import__(
            f"plugin.{plugin_name}", fromlist=[plugin_name]
        )  # 动态加载
        t_plugin = plugin.ProxyPlugin()
        plugin_list.append(t_plugin)  # 保活
        apscheduler.add_job(
            task_crawler_proxy,
            "interval",
            seconds=t_plugin.interval,
            next_run_time=datetime.datetime.now(),
            args=[t_plugin],
        )
    apscheduler.add_job(
        task_check_thread,
        "interval",
        seconds=3,
        next_run_time=datetime.datetime.now(),
    )  # 检测进程
    apscheduler.add_job(
        task_check_local_proxy,
        "interval",
        seconds=1,
        next_run_time=datetime.datetime.now(),
    )  # 本地代理监控进程
    apscheduler.start()
