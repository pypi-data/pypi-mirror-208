from setuptools import setup, find_packages

VERSION = '0.0.84'

# 导入信息说明文档
with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setup(
    name='xToolkit',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    entry_points={},
    # 依赖库，格式为 arrow 或者 arrow>=0.13.2
    install_requires=[
        "python-dateutil>=2.8.1",  # 时间操作库
        "jieba>=0.42.1",  # 中文分词库
        "numpy>=1.19.5",  # 这个地方填1.19.5，因为linux里面numpy最高版本为1.19.5
        "pandas>=1.1.1",
        "emoji>=0.6.0",  # emoji图标库
        "xlrd>=1.2.0",  # 读excel库
        "xlwt>=1.3.0",  # 写excel库
    ],
    # 项目相关文件地址，一般是github
    url='https://github.com/xionglihong/xToolkit',
    # 许可证
    license='GNU General Public License v3.0',
    # 作者
    author='xionglihong',
    # 作者邮箱
    author_email='xionglihong@163.com',
    # 项目详细描述
    long_description=long_description,
    long_description_content_type="text/markdown",
)
