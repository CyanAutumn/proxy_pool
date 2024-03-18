from utils import flogger
from utils import database
from utils import proxy_tools
from utils.proxy_plugin_base import ProxyPlugin
from utils.web_request import webRequest


class ProxyPlugin(ProxyPlugin):
    log = flogger.Flogger().get_logger(__name__)

    def get_proxy(self):
        info_key = [
            "ip",
            "port",
            "level",
            "type",
            "location",
            "time_out",
            "last_used_time",
        ]
        for type in range(2):
            for page in range(7):
                html = (
                    webRequest()
                    .get(f"http://www.ip3366.net/free/?stype={type+1}&page={page+1}")
                    .get_html("gb2312")
                )
                proxy_list = []
                ele_info_row_list = html.xpath('//*[@id="list"]/table/tbody/tr')
                for ele_info_raw in ele_info_row_list:
                    info_value = []
                    for ele_info in ele_info_raw.xpath("td"):
                        t = ele_info.xpath("text()").get()
                        info_value.append(t)
                    proxy = dict(zip(info_key, info_value))
                    proxy["time_out"] = proxy.get("time_out", "0秒").replace("秒", "")
                    proxy_list.append(proxy_tools.convert_dict_to_proxy(proxy))
                yield proxy_list


if __name__ == "__main__":
    for proxy_list in ProxyPlugin().get_proxy():
        print(proxy_list)
