from sqlalchemy import create_engine, MetaData, Table, delete, and_
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect
import pandas as pd


class DBUpdater:
    """
    Mysql数据更新脚本,根据设定好的Keys,更新数据表,等于是覆盖之前的数据

    uri = "mysql+pymysql://user:password@127.0.0.1:3306/db"
    keys = ["日期", "账户", "推广计划ID"]
    table_name = "baidu_sem"  # 数据表

    # Assume df is your DataFrame
    updater = DBUpdater(uri, keys)
    updater.update(df, table_name)
    updater.close()

    使用场景: 导入数据,用于做分析


    """

    def __init__(self, uri, keys):
        self.engine = create_engine(uri)
        self.keys = keys
        self.meta = MetaData()

    def close(self):
        self.engine.dispose()

    def update(self, df, table_name):
        if not inspect(self.engine).has_table(table_name):
            df.to_sql(table_name, self.engine, index=False)
            # 这个主键就不设置了,直接导入就可以
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
