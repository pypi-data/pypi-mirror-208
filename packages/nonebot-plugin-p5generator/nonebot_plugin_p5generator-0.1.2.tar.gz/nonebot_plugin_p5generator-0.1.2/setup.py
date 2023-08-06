# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_p5generator']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.2.0,<3.0.0',
 'nonebot2>=2.0.0rc2,<3.0.0',
 'pillow>=9.5.0,<10.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-p5generator',
    'version': '0.1.2',
    'description': 'A generator of persona5 chatbot based on nonebot2 framework',
    'long_description': '<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# nonebot-plugin-p5generator\n\n《女神异闻录5》预告信的生成插件\n\n</div>\n\n## 💬 前言\n\n可以生成仿《女神异闻录5》中心之怪盗团向罪人宣战的预告信，做的不太好请见谅\n\n## 📖 介绍\n\n使用Pillow库制作的一款插件，因为p5中的预告信字都是从报纸上面剪下来的，所以还原了随机的字体。\n代码比较烂，随便看看吧。\n知识和勇气增加了。\n\n## 💿 安装\n\n<details>\n<summary>nb-cli安装</summary>\n在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装\n  \n    nb plugin install nonebot-plugin-p5generator\n\n</details>\n\n<details>\n<summary>pip安装</summary>\n  \n    pip install nonebot-plugin-p5generator\n\n</details>\n\n## 🍰 资源文件\n\n`data`文件夹中的`p5generator`会存储与插件有关的文件\n\n下载仓库中p5generator文件夹后放入data文件夹中\n\n## 🎉 使用\n\n输入`p5预告信`后接你想要输入的内容即可生成：\n\n![946CE1499E017FE129710E8B6E2FB725](https://github.com/xi-yue-233/nonebot-plugin-p5generator/assets/58218656/0a19bacc-bde4-4693-93e7-83678bde4835)\n\n![5C4D9FCBE4F060A12612D6062287E7E6](https://github.com/xi-yue-233/nonebot-plugin-p5generator/assets/58218656/4aade3a7-34a0-4e81-96ea-612146b76808)\n',
    'author': 'xi-yue-233',
    'author_email': '1004514855@qq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
