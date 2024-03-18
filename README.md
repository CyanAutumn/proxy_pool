# proxy_pool

    2024年3月18日：
    因几乎所有代理网站抓取的代理都仅支持http而不支持https，个人已改用收费代理，此项目已废弃
    如果你有需要用到http代理的需求，可以更改 utils\proxy_tools.py 中的代理验证部分代码，将相关校验地址改为http即可

一个简易的代理池，从以下网站获取代理，经过验证后进行入库操作，并周期性的验证库中存放超过一定时长的代理，剔除无效代理

| 网站名 | 链接 |
|:--|:--|
| 89免费代理 | https://www.89ip.cn/ |
| 开心代理 | http://www.kxdaili.com/ |
| 快代理 | https://www.kuaidaili.com/ |
| 齐云代理 | https://proxy.ip3366.net/ |
| 云代理 | http://www.ip3366.net// |

## 如何开始

```bash
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 如何新增代理网站爬虫插件

代理网站的爬虫插件存放在 ./plugin 目录中，如果你想要新增代理插件，只需要在该目录下创建相关文件，其中的类继承 ./utils/proxy_plugin_base.py ，并重写实现 get_proxy() 函数即可

以下是一个新插件的模板

```python
from utils import flogger
from utils import proxy_tools
from utils.proxy_plugin_base import ProxyPlugin


class ProxyPlugin(ProxyPlugin):
    log = flogger.Flogger().get_logger(__name__)

    def get_proxy(self):
        proxy_list=[] #这里是你获取到的代理列表，是一个dict的list
        proxy_list.append(proxy_tools.convert_dict_to_proxy(proxy)) # 获取到应该为dict，在这里转换成数据库中间件的内置格式，key值必须包含ip,port,location,type(大写的HTTP,HTTPS，用逗号隔开)
        yield proxy_list 
```