from pandas import read_csv, to_datetime
from sqlalchemy import create_engine, MetaData, Table, delete, and_
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect
import pandas as pd
import os
import glob
from pandas import read_excel
import shutil

import tybase

class DataFrameProcessor:
    """
    DataFrameProcessor 类设计用于根据特定规则处理 CSV 文件中的数据。

    属性:
        config_df: 一个 pandas DataFrame 对象，用于存储配置数据。
    用处:
        封装了一些基本的数据导入的时候会用到的转换函数

    """

    def __init__(self, config_file_path):
        """使用配置数据初始化 DataFrameProcessor 类。"""
        self.config_df = read_csv(config_file_path)

    def _extract_app_name(self, account):
        """
        私有辅助方法，根据账户名称提取对应的应用名称。

        参数:
            account: 字符串类型，账户名称。

        返回:
            字符串类型，对应的应用名称。
        """
        return self.config_df[self.config_df.账户名称 == account].iloc[0]["推广APP"]

    @staticmethod
    def _percentage_to_float(percentage):
        """
        私有辅助方法，将百分比字符串转化为浮点数。

        参数:
            percentage: 字符串类型，百分比字符串。

        返回:
            浮点数类型，百分比浮点数。
        """
        percentage = percentage.replace("%", "")
        return round(float(percentage) / 100, 3)

    @staticmethod
    def _identify_operating_system(plan):
        """
        私有辅助方法，根据推广计划识别操作系统。

        参数:
            plan: 字符串类型，推广计划。

        返回:
            字符串类型，识别出的操作系统。
        """
        if "IOS" in plan:
            return "IOS"
        else:
            return "安卓"

    @staticmethod
    def _rename_columns(df, column_mapping):
        """
        私有辅助方法，根据提供的映射关系重命名 DataFrame 的列。

        参数:
            df: pandas DataFrame 对象。
            column_mapping: 字典类型，列名的映射关系。

        返回:
            pandas DataFrame 对象。
        """
        return df.rename(columns=column_mapping)


class BaiduImport(DataFrameProcessor):
    """
    BaiduImport 类设计用于处理百度推广的 CSV 文件。

    属性:
        config_df: 一个 pandas DataFrame 对象，用于存储配置数据。

    使用方法:
        processor = BaiduImport("config.csv")
        df = processor.process_csv("jihua_20230505-20230511_47190093_861922.csv", {"注册人数(转化时间)":"注册数"})
    """

    def __init__(self, config_file_path):
        """使用配置数据初始化 BaiduImport 类。"""
        super().__init__(config_file_path)

    def process_plan_csv(self, file_path, column_mapping=None):
        """
        处理百度搜索计划导入,这里封装的一般流程,如果需要分析的话,需要把这里字符串的处理逻辑改一下
         CSV 文件并返回一个 pandas DataFrame 对象。

        参数:
            file_path: 字符串类型，CSV 文件的路径。
            column_mapping: 字典类型，列名的映射关系。

        返回:
            pandas DataFrame 对象。
        """
        df = read_csv(file_path, encoding='gbk', skiprows=5)
        # df["APP"] = df["账户"].apply(self._extract_app_name)
        df["上方展现胜出率"] = df["上方展现胜出率"].str.replace("-", "0")
        df["上方展现胜出率"] = df["上方展现胜出率"].apply(self._percentage_to_float)
        df["点击率"] = df["点击率"].apply(self._percentage_to_float)
        df['日期'] = to_datetime(df['日期'])
        df["操作系统"] = df["推广计划"].apply(self._identify_operating_system)
        df["推广计划ID"] = df["推广计划ID"].astype(str)

        my_col = ['日期', '推广计划ID', '账户', '推广计划', '展现', '点击', '消费', '点击率', '平均点击价格',
                  '激活人数（转化时间）', '注册人数（转化时间）', '激活30日内付费金额（转化时间）', '上方展现胜出率',
                  '付费次数（转化时间）',
                  '付费转化价值（转化时间）', '操作系统']
        df = df[my_col]

        # 把config的信息也导入进来
        config_dict = self.config_df[self.config_df.账户名称 == df.账户[0]].iloc[0]
        df["返点"] = config_dict["返点"]
        df["代理商"] = config_dict["代理商"]
        df["APP"] = config_dict["推广APP"]

        # 如果提供了列名映射关系，则重命名列名
        if column_mapping is not None:
            df = self._rename_columns(df, column_mapping)

        return df


class DBUpdater:
    def __init__(self, uri, keys):
        self.engine = create_engine(uri)
        self.keys = keys
        self.meta = MetaData()

    def close(self):
        self.engine.dispose()

    def update(self, df, table_name):
        if not inspect(self.engine).has_table(table_name):
            df.to_sql(table_name, self.engine, index=False)
            # with self.engine.connect() as con:
            #     con.execute(f'ALTER TABLE {table_name} ADD PRIMARY KEY ({" ,".join(self.keys)});')

        else:
            table = Table(table_name, self.meta, autoload_with=self.engine)
            with self.engine.connect() as connection:
                trans = connection.begin()  # 开始事务

                try:
                    for _, row in df.iterrows():
                        where_condition = ' AND '.join([f"{key} = '{row[key]}'" for key in self.keys])
                        stmt = text(f"SELECT * FROM {table_name} WHERE {where_condition}")
                        result = connection.execute(stmt)
                        if result.rowcount > 0:
                            del_stmt = text(f"DELETE FROM {table_name} WHERE {where_condition}")
                            connection.execute(del_stmt)
                    trans.commit()  # 提交事务
                except:
                    trans.rollback()  # 如果发生错误，则回滚事务
                    raise

        df.to_sql(table_name, self.engine, if_exists='append', index=False)


class DirectoryProcessor:
    """
    # 使用方式：
        # 导入配置文件
        #configh.csv的字段:
            #账户名称,推广APP,返点,代理商,密码
        from tybase.dbtool.data_import BaiduImport,DirectoryProcessor
        baidu_processor = BaiduImport("config.csv")  # BaiduImport 可以通过重写 process_plan_csv 来解决处理更多的格式

        # 定义需要映射的处理字段
        column_mapping = {"注册人数（转化时间）": "注册数",
                          "激活人数（转化时间）":"激活数",
                          "付费次数（转化时间）":"付费次数",
                          "激活30日内付费金额（转化时间）":"付费金额",
                          "付费转化价值（转化时间）":"付费转化价值"
                         }
        # 写好Mysql URI
        uri = "mysql+pymysql://user:pwd@ip:port/db"
        keys = ["日期", "账户", "推广计划ID"]   # 不重复导入的字段判断
        table_name = "baidu_sem"   # 导入的表名

        directory_processor = DirectoryProcessor("待上传", "上传成功",
                                                 baidu_processor, column_mapping, uri, keys, table_name)
        directory_processor.process_directory()

    """

    def __init__(self, directory, backup_directory, processor, column_mapping, uri, keys, table_name):
        self.directory = directory
        self.backup_directory = backup_directory
        self.processor = processor
        self.column_mapping = column_mapping
        self.uri = uri
        self.keys = keys
        self.table_name = table_name
        os.makedirs(self.backup_directory, exist_ok=True)  # 创建备份文件夹，如果还不存在的话

    def process_directory(self):
        for file_path in glob.glob(os.path.join(self.directory, '*')):
            _, ext = os.path.splitext(file_path)
            if ext in ['.csv', '.xlsx']:
                print(f"开始处理文件: {file_path}")
                try:
                    if ext == '.csv':
                        df = self.processor.process_plan_csv(file_path, self.column_mapping)
                    else:  # .xlsx
                        df = read_excel(file_path)
                        df = self.processor.process_plan_csv(df, self.column_mapping)
                    print(f"文件处理成功, 开始更新数据库...")
                    updater = DBUpdater(self.uri, self.keys)
                    updater.update(df, self.table_name)
                    updater.close()
                    print(f"数据库更新成功, 移动文件到备份文件夹...")
                    shutil.move(file_path, self.backup_directory)  # 把处理成功的文件移动到备份文件夹
                    print(f"文件移动成功")
                except Exception as e:
                    print(f"处理文件 {file_path} 出错: {e}")
                    import traceback
                    traceback.print_exc()
