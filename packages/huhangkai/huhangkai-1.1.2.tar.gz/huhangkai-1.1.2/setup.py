from setuptools import setup, find_packages

setup(
    name='huhangkai',  # 对外模块的名字
    version='1.1.2',  # 版本号
    description='接口自动化',  # 描述
    author='胡杭凯',  # 作者
    author_email='3173825608@qq.com',
    # package_dir={"": "commen"},
    packages=find_packages(),
    package_data={'by': ['常用命令.bat'],},
    python_requires=">=3.0",
    install_requires=[
        "faker",
        "requests",
        "openpyxl"
    ],
)