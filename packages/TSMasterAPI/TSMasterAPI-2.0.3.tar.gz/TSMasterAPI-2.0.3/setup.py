'''
Author: seven 865762826@qq.com
Date: 2023-03-24 09:26:29
LastEditors: seven 865762826@qq.com
LastEditTime: 2023-05-17 14:17:11
FilePath: \VSCode_Pro\Python_Pro\TSMasterApi\setup.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r",encoding="utf-8") as f:
  long_description = f.read()

# 
setup(name='TSMasterAPI',  # 包名
      version='2.0.3',  # 版本号
      description='Use TSMaster hardware',
      long_description=long_description,
      author='seven',
      author_email='865762826@qq.com',
      install_requires=[],
      license='BSD License',
      packages=find_packages(),
      platforms=["WINDOWS"],
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Software Development :: Libraries'
      ],
      )
