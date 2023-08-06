from setuptools import setup, find_packages 
import codecs
import os 

name='pipetool'

def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), "r",encoding='utf-8').read()


def get_version(): 
    version_file = name + '/version.py'
    with open(version_file, 'r', encoding='utf-8') as f:
        exec(compile(f.read(), version_file, 'exec'))
    return locals()['__version__']
    '''
    return '0.0.1'
    '''

setup(
    name=name,
    version=get_version(),
    description="基础工具集，统一文件读写，规范流行线过程",
    author='zhys513',#作者
    packages=find_packages(),
    author_email="254851907@qq.com",
    url="https://gitee.com/zhys513/pipetool",
    python_requires='>=3.6', 
    install_requires=['addict','yapf','pyyaml','regex','packaging','loguru'],
)

