from setuptools import setup, find_namespace_packages


readme = ''

setup(
    description='',
    long_description=readme,
    name='bkapi-plugins-py', # 包的名字
    version='0.0512', # 版本号每次打包完要改一下
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
    author='fadewalk',
    license='Apach License 2.0',
    # packages=find_packages(),
    # namespace_packages=['bkapi_plugins'],
    package_dir={'': '.'},
    include_package_data=True,
    package_data={ # 包的数据，可以不写
        # 'bkapi_plugins': ['data.zip','generator1.0.tar.gz'],
        # 'bkapi_plugins': ['generator1.0.tar.gz'],
    },
    #  packages= find_namespace_packages(
    #             include=["bkapi_plugins", "bkapi_plugins.*"], ),
    # install_requires=[
    #     'bkapi-client-core>=1.1.0,<2.0.0',
    # ],
)
