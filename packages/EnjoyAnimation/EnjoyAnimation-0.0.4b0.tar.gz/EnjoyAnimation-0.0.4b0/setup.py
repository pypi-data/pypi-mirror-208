from setuptools import setup, find_packages

with open("README.md", "r",encoding="utf-8") as readme_file:
    readme = readme_file.read()

requirements = ["bs4","requests"] # 这里填依赖包信息
VERSION="0.0.4b0"

setup(
    name="",
    version=VERSION,
    author="slexce",
    author_email="sim69732@gmail.com",
    description="基于nonebot与gocqhttp的动漫番剧插件",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/small-bili/nonebot-plugin-EnjoyAnimation",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
	"Programming Language :: Python :: 3.10",
	"License :: OSI Approved :: MIT License",
    ],
)