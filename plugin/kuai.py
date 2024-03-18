import json
from utils import flogger
from utils import database
from utils import proxy_tools
from utils.proxy_plugin_base import ProxyPlugin
from utils.web_request import webRequest


class ProxyPlugin(ProxyPlugin):
    log = flogger.Flogger().get_logger(__name__)

    def get_proxy(self):
        for type in ["inha", "intr"]:
            for page in range(20):  # 20页之后的没有意义，浪费资源
                text_html = (
                    webRequest()
                    .get(f"https://www.kuaidaili.com/free/{type}/{page+1}")
                    .text
                )
                str_start = "const fpsList = "
                str_end = "}]"
                idx_start = text_html.find(str_start)
                text_html = text_html[idx_start + len(str_start) :]
                idx_end = text_html.find(str_end)
                text_html = text_html[: idx_end + len(str_end)]
                t_proxy_list = json.loads(text_html)
                proxy_list = []
                for t_proxy in t_proxy_list:
                    t_proxy["time_out"] = str(t_proxy.pop("speed") / 1000.0)
                    t_proxy["type"] = "HTTP"  # 网站只有HTTP类型的免费代理
                    proxy_list.append(proxy_tools.convert_dict_to_proxy(t_proxy))
                yield proxy_list


if __name__ == "__main__":
    for proxy_list in ProxyPlugin().get_proxy():
        print(proxy_list)
