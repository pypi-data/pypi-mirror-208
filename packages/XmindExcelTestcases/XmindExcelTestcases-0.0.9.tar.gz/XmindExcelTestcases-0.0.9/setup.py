import setuptools

# 读取项目的readme介绍
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="XmindExcelTestcases",# 项目名称，保证它的唯一性，不要跟已存在的包名冲突即可
    version="0.0.9",
    author="kaven.xue", # 项目作者
    author_email="454086662@qq.com",
    description="xmind脑图转换为Excel格式的测试用例", # 项目的一句话描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",# 项目地址
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'XmindExcelTestcases = XmindExcelTestcases.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

requires = [
    'xmindparser',
    'pandas'
]

