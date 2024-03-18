from flask import Flask
from utils import proxy_core
from utils import proxy_tools
from utils import database
from utils.web_request import webRequest

app = Flask(__name__)


@app.route("/get_proxy/<int:num>", methods=["GET"])
def get_proxy(num):
    """提取指定数量的ip"""
    proxy_list = database.get_proxy(num)
    _ = []
    for proxy in proxy_list:
        _.append(proxy_tools.convert_proxy_to_dict(proxy))
    return _


if __name__ == "__main__":
    database.init()
    proxy_core.run()
    app.run(host="0.0.0.0", port=5000, debug=False)
