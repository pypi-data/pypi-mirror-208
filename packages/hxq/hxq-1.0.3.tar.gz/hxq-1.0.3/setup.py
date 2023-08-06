from setuptools import find_packages, setup

setup(name='hxq',
      author='hxq',
      version='1.0.3',
      packages=find_packages(exclude=["*.demo", "*.demo.*", "tests", "demos"]),
      author_email='337168530@qq.com',
      description="这是一个python工具包",
      license="GPL",
      # 而 extras_require 这里仅表示该模块会依赖这些包,深度使用模块时，才会用到，这里需要你手动安装
      extras_require={
          'HTML': ["bs4>=0.0.1", "xmltodict>=1.2"],
      },
      # install_requires 在安装模块时会自动安装依赖包
      install_requires=[
          'requests==2.24.0',
          'lxml==4.9.2',
          'pymysql==1.0.3',
          'DBUtils==3.0.2',
          'aiofiles==23.1.0',
          'winshell==0.6'
      ]
      )
