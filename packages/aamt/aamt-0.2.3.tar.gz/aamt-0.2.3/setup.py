# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aamt']

package_data = \
{'': ['*']}

install_requires = \
['allure-pytest>=2.12.0,<3.0.0',
 'colorlog>=6.7.0,<7.0.0',
 'faker>=15.3.3,<16.0.0',
 'jmespath>=1.0.1,<2.0.0',
 'pytest>=7.2.0,<8.0.0',
 'pyyaml>=6.0,<7.0',
 'sqlalchemy>=1.4.44,<2.0.0',
 'texttable>=1.6.7,<2.0.0']

entry_points = \
{'console_scripts': ['aamt = aamt.cli:main'],
 'pytest11': ['aamt = aamt.plugin:Plugin']}

setup_kwargs = {
    'name': 'aamt',
    'version': '0.2.3',
    'description': '基于pytest的接口自动化测试工具模板',
    'long_description': '## AAMT 项目模版\n> 用于生成 基于pytest的接口自动化脚手架\n\npython 版本\n\n> 3.9\n\n安装最新版本\n\n> pip install aamt\n\n指定版本安装\n\n> pip install aamt==0.2.2\n\n升级aamt\n\n> pip install -U aamt\n\n创建项目脚手架 \n\n> aamt startproject demo\n\n创建项目脚手架(自动创建虚拟环境)\n\n> aamt startproject demo -venv\n\n外网速度慢，pandas可能安装失败，推荐用国内镜像\n\n> pip --default-timeout=6000 install -i https://pypi.tuna.tsinghua.edu.cn/simple aamt\n\n\n\n',
    'author': 'xuefeng365',
    'author_email': '120158568@qq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/xuefeng365/aamt-template.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
