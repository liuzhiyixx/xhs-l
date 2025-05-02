import time
import pandas as pd
import json  # 导入json模块
from DrissionPage import WebPage
from DrissionPage.common import Actions

wp = WebPage()
ac = Actions(wp)

# 打开小红书页面  此处是用户自己登录
wp.get('https://www.xiaohongshu.com')

wp.refresh()  # 刷新页面
