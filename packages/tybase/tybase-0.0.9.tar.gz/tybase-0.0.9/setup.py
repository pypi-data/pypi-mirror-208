from setuptools import setup, find_packages

setup(
    name='tybase',
    version='0.0.9',
    include_package_data=True,
    description='简单优化了一下导入的方法',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',  # 版本描述
    author='Tuya',
    author_email='353335447@qq.com',
    url='https://github.com/yourusername/your_package',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'requests',
        "pymysql",
        "mysql-connector-python",
        "sqlalchemy",
        "pandas",
        "langchain",
        "openai"
        # List your package dependencies here
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
)
