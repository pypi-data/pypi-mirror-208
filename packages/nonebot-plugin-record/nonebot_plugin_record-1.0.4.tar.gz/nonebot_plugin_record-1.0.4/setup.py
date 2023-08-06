# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_record']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.3,<0.24.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'pilk>=0.2.3,<0.3.0']

setup_kwargs = {
    'name': 'nonebot-plugin-record',
    'version': '1.0.4',
    'description': '基于 Nonebot2 的语音功能适配插件，包括语音事件响应器，语音识别、语音合成等功能',
    'long_description': '<div align="center">\n  <a href="https://v2.nonebot.dev/store"><img src="https://s2.loli.net/2022/06/16/opBDE8Swad5rU3n.png" width="180" height="180" alt="NoneBotPluginLogo"></a>\n  <br>\n  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>\n</div>\n\n<div align="center">\n\n# Nonebot-Plugin-Record\n\n_✨ 基于 [NoneBot2](https://v2.nonebot.dev/) 的语音功能适配插件 ✨_\n\n<p align="center">\n  <img src="https://img.shields.io/github/license/itsevin/nonebot_plugin_record" alt="license">\n  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">\n  <img src="https://img.shields.io/badge/nonebot-2.0.0b4+-red.svg" alt="NoneBot">\n  <a href="https://pypi.org/project/nonebot-plugin-record">\n    <img src="https://badgen.net/pypi/v/nonebot-plugin-record" alt="pypi">\n  </a>\n</p>\n\n</div>\n\n## 功能\n\n- 语音事件响应器（仅限私聊）\n- 语音识别（仅限私聊，支持百度智能云、腾讯云接口）\n- 语音合成（利用TX的tts接口）\n\n## 安装\n\n- 使用 nb-cli\n\n```\nnb plugin install nonebot-plugin-record\n```\n\n- 使用 pip\n\n```\npip install nonebot_plugin_record\n```\n\n## 配置项\n\n```\nasr_api_provider="" #必填，API提供商，填写“baidu”或“tencent”\nasr_api_key="" #必填，百度智能云的API_KRY或腾讯云的SECRET_ID\nasr_secret_key="" #必填，百度智能云的SECRET_KRY或腾讯云的SECRET_KEY\nnonebot_plugin_gocqhttp=False #选填，是否使用nonebot2插件版本的go-cqhttp，默认为False\n```\n\n## API选择与配置\n\n### 选什么API?\n\n- 百度智能云-短语音识别标准版：5并发，15万次免费调用量，期限180天\n- 腾讯云-一句话识别：每月5000次免费调用量（推荐）\n\n### 获取密钥\n\n- 百度智能云：https://ai.baidu.com/tech/speech\n- 腾讯云：https://cloud.tencent.com/document/product/1093\n\n## 如何使用？\n\n### 语音事件响应器的使用\n\n语音事件响应器：```on_record()```\n\n说明：语音事件响应器继承自```on_message```，在其上增加了自定义的相应事件响应规则\n\n选填参数：\n\n```\nrule: 事件响应规则\npermission: 事件响应权限\nhandlers: 事件处理函数列表\ntemp: 是否为临时事件响应器（仅执行一次）\nexpire_time: 事件响应器最终有效时间点，过时即被删除\npriority: 事件响应器优先级\nblock: 是否阻止事件向更低优先级传递\nstate: 默认 state\n```\n\n代码示例：\n\n```python\n# 导入依赖包\nfrom nonebot import require\nrequire(\'nonebot_plugin_record\')\nfrom nonebot_plugin_record import on_record\n\n# 注册语音事件响应器\nmatcher = on_record()\n```\n\n### 获取语音中的文本\n\n获取文本的异步函数：```get_text```()\n\n必填参数：\n\n```\nbot: Bot 对象\nevent: Event 对象\n```\n\n代码示例：\n\n```python\n# 导入依赖包\nfrom nonebot import require\nrequire(\'nonebot_plugin_record\')\nfrom nonebot_plugin_record import get_text\nfrom nonebot.adapters.onebot.v11 import Event, Bot\n\n# 事件处理中获取文本\ntext = await get_text(bot=bot, event=event)\n```\n\n> 当函数出错时会返回None，具体报错信息请前往Nonebot2进程日志查看\n\n### 获取文本转换的语音的```Message```对象\n\n获取文本转换的语音的Message对象的异步函数：```record_tts```()\n\n必填参数：\n```\npatter: 要进行转换的字符串\n```\n\n代码示例：\n\n```python\n# 导入依赖包\nfrom nonebot import require\nrequire(\'nonebot_plugin_record\')\nfrom nonebot_plugin_record import record_tts\n\n# 事件处理中获取文本转换的语音的Message对象\nrecord_tts(pattern=pattern)\n```\n\n### 插件示例\n\n私聊语音聊天插件：\n\n```python\nfrom nonebot.adapters.onebot.v11 import (\n    Event,\n    Bot\n)\nfrom nonebot import require\nrequire(\'nonebot_plugin_record\')\nfrom nonebot_plugin_record import (\n    on_record,\n    get_text,\n    record_tts\n)\n\nimport httpx\nimport json\n\n\nchat = on_record()\n\n\n@chat.handle()\nasync def main(bot: Bot, event: Event):\n    text = await get_text(bot, event)\n    msg = await get_data(text)\n    await chat.finish(record_tts(msg))\n\n\nasync def get_data(msg):\n    url = f\'http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}\'\n    async with httpx.AsyncClient() as client:\n        resp = await client.get(url)\n        get_dic = json.loads(resp.text)\n    data = get_dic[\'content\']\n    return data\n\n```\n\n## 有问题怎么办？\n\n1. 确认是不是你自己的插件的问题\n2. 确认是否正确按照本插件使用说明使用\n3. 排查日志，通过日志内容尝试找出问题并自行解决\n4. 在配置文件中配置```LOG_LEVEL=DEBUG```，然后在日志中查看debug日志，并同时根据本插件源码尝试找出问题并自行解决（确认是本插件的问题可以提issue或者pr）\n5. 问题仍未解决可以提issue，要求提供详细问题描述和较为完整的debug级别的相关日志\n\n## 更新日志\n\n### 2023/5/13 \\[v1.0.4]\n\n- 重构代码，舍弃CQ码过时写法\n- 增加dubug和info级别的日志输出\n\n### 2023/1/27 \\[v1.0.3]\n\n- 修复错误\n\n### 2023/1/15 \\[v1.0.2]\n\n- 修复错误\n\n### 2023/1/15 \\[v1.0.1]\n\n- 适配Nonebot2商店插件自动检测，删除配置文件报错提醒\n\n### 2023/1/15 \\[v1.0.0]\n\n- 发布插件\n',
    'author': 'ITSevin',
    'author_email': 'itsevin@qq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/itsevin/nonebot_plugin_record',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
