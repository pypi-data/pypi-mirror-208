from setuptools import setup, find_packages

APP = ['ultipa']
DATA_FILES = []
OPTIONS = {}

def readMe():
    try:
        ret = open('/Users/ultipa/work/MakeUltipaPackage/ReadMe.md', encoding="utf-8").read()
    except Exception as e:
        return ""
    return ret

setup(
    app=APP,
    name="ultipa",
    version="4.3.1",
    python_requires='>=3.6, <=3.10',
    packages=find_packages(),  # 常用,要熟悉 :会自动查找当前目录下的所有模块(.py文件) 和包(包含__init___.py文件的文件夹)
    # scripts = ['say_hello.py'],
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
                'grpcio==1.48.2',
                'grpcio-tools==1.48.2',
                'protobuf==3.19.0',
                'google==2.0.3',
                'schedule==1.1.0',
                'prettytable==2.5.0',
                'treelib==1.6.1',
                "tzlocal==4.2",
                "pytz==2022.7",
                "future~=0.18.2",
                "python-dateutil~=2.8.2"
                ],  # 常用
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst',"printer"],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },
    # metadata for upload to PyPI
    author="Ultipa",
    author_email="support@ultipa.com",
    description="Pure Python Ultipa Driver",
    license="PSF",
    keywords="ultipa sdk,ultipa graph",
    url="https://www.ultipa.com/document/ultipa-drivers/python-installation",  # project home page, if any
    long_description=readMe(),
    long_description_content_type='text/markdown',
    # could also include long_description, download_url, classifiers, etc.
)
