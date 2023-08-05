# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['idcode']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['idcode = idcode.cli:main']}

setup_kwargs = {
    'name': 'idcode',
    'version': '0.1.4',
    'description': '交互式检测并解码编码文本。',
    'long_description': '# idcode\n\nidcode 是一个使用 Python 编写的命令行工具，用于交互式检测并解码编码文本。它支持命令行输入和文件输入，可以自动检测编码类型和尝试解码，并提供了一个交互式界面来逐步解码编码文本。\n\n## 支持的编码格式\n\nidcode 支持多种编码格式，包括：\n\n- Base85/Base64/Base32\n- Base94/Base92/Base91/Ascii85/AdobeAscii85/Z85/Base58/Base45/Base36/Base8\n- Binary 编码\n- ASCII 编码\n- Hex 编码\n- URL 编码\n- HTML 实体编码\n- Quoted-printable 编码\n- 核心价值观编码\n\n## 安装\n\n从 PyPi 安装：\n\n```sh\npip install idcode\n```\n\n## 用法\n\nidcode 支持交互式输入、命令行输入和文件输入来获取编码文本。\n\n### 交互式输入\n\n当不给出任何命令行参数时，程序会在运行后提示你给出目标文本：\n\n```sh\nidcode\n```\n\n### 命令行输入\n\n要使用命令行输入方式来解码编码文本，你可以运行以下命令：\n\n```sh\nidcode -t "编码文本"\n```\n\n其中，`-t` 参数用于指定要解码的文本。\n\n### 文件输入\n\n要使用文件输入方式来解码编码文本，你可以运行以下命令：\n\n```sh\nidcode -f "文件路径"\n```\n\n其中，`-f` 参数用于指定包含编码文本的文件路径。\n\n## 贡献\n\n如果你发现了 bug，或者有改进建议，请随时创建 issue 或者 pull request。我们欢迎任何形式的贡献。\n\n## 许可证\n\nidcode 使用 MIT 许可证。请参阅 LICENSE 文件了解更多详情。',
    'author': 'p0ise',
    'author_email': 'changelf@163.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/p0ise/idcode',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
