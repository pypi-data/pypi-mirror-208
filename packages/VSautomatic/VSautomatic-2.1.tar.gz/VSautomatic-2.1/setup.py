import setuptools
 
# requirements = ['numpy']       # 自定义工具中需要的依赖包
 
setuptools.setup(
    name="VSautomatic",       # 自定义工具包的名字
    version="2.1",             # 版本号
    author="jasonliu",           # 作者名字
    author_email="batianhu4444@gmail.com",  # 作者邮箱
    description="VS Automatic Tools", # 自定义工具包的简介
    license='MIT-0',           # 许可协议
    url="https://pypi.org/manage/projects/",              # 项目开源地址
    packages=setuptools.find_packages(),  # 自动发现自定义工具包中的所有包和子包
    # install_requires=requirements,  # 安装自定义工具包需要依赖的包
    package_data={'': ['*.csv','*.txt','*.toml','*.exe','*.xml','*.config','*.dll','*.pyc']},  #这个很重要,如果你的包里，需要读出原目录中相关的.txt,csv,toml等格式文件，这个你要记得带上
    python_requires='>=3.9'         # 自定义工具包对于python版本的要求
    
)