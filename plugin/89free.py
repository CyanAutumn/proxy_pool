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
            "location",
            "operator",
            "last_used_time",
        ]
        for page in range(1):
            html = (
                webRequest()
                .get(f"https://www.89ip.cn/index_{page+1}.html", timeout=10)
                .html
            )
            proxy_list = []
            ele_info_row_list = html.xpath('//div[@class="layui-form"]/table/tbody/tr')
            for ele_info_raw in ele_info_row_list:
                info_value = []
                for ele_info in ele_info_raw.xpath("td"):
                    t = ele_info.xpath("text()").get()
                    t = t.replace("\n", "").replace("\t", "").strip()
                    info_value.append(t)
                proxy = dict(zip(info_key, info_value))
                proxy["location"] = proxy["location"] + proxy["operator"]
                proxy["type"] = "HTTP"
                proxy_list.append(proxy_tools.convert_dict_to_proxy(proxy))
            yield proxy_list


if __name__ == "__main__":
    for proxy_list in ProxyPlugin().get_proxy():
        print(proxy_list)
