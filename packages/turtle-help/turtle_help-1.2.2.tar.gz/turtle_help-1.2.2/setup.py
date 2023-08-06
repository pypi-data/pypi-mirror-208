from distutils.core import  setup
import setuptools
packages = ['turtle_help']# 唯一的包名，自己取名
setup(name='turtle_help',
	version='1.2.2',
	author='DanJamesThomas',
    packages=packages, 
    package_dir={'requests': 'requests'},)
