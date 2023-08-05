from setuptools import setup, find_packages 
import codecs,os

name='gradiop'
   

def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), "r",encoding='utf-8').read()


def get_version(): 
    version_file = name + '/version.py'
    with open(version_file, 'r', encoding='utf-8') as f:
        exec(compile(f.read(), version_file, 'exec'))
    return locals()['__version__']
    '''
    return '0.0.2'
    '''  

setup(
    name=name,
    version=get_version(),
    description="gradio 本地部署 插件",
    author='zhys513',#作者
    packages=find_packages(), 
    author_email="254851907@qq.com",
    url="https://gitee.com/zhys513/gradio_plug",
    python_requires='>=3.6', 
    install_requires=['gradio'],
    # 任何包如果包含 *.txt or *.rst 文件都加进去，可以处理多层package目录结构 
    package_data={
        'gradiop': ['templates/*.js', 'templates/*.css', 'templates/*.map'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': ['gradiop=gradiop.plug:install']
    },
 
)
 
