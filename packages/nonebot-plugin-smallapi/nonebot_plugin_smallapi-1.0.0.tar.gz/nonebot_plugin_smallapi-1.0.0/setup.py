import setuptools #导入setuptools打包工具

install_requires=['jsonpath','nonebot2[aiohttp]','httpx'],

setuptools.setup(
    name="nonebot_plugin_smallapi", # 用自己的名替换其中的YOUR_USERNAME_
    version="1.0.0",    #包版本号，便于维护版本
    author="Chaichaisi",    #作者，可以写自己的姓名
    author_email="chaichaisi@qq.com",    #作者联系方式，可写自己的邮箱地址
    description="A small nonebot_plugin_smallapi plugin",#包的简述
    long_description="come in to read more",    #包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="https://github.com/chaichaisi/nonebot_plugin_smallapi",    #自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',    #对python的最低版本要求
)
