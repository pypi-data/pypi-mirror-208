'''
python的数据库模块有统一的接口标准，所以数据库操作都有统一的模式，基本上都是下面几步（假设数据库模块名为db）：

1. 用db.connect创建数据库连接，假设连接对象为conn
2. 如果该数据库操作不需要返回结果，就直接用conn.execute查询，根据数据库事务隔离级别的不同，可能修改数据库需要conn.commit
3. 如果需要返回查询结果则用conn.cursor创建游标对象cur, 通过cur.execute查询数据库，用cur.fetchall/cur.fetchone/cur.fetchmany返回查询结果。根据数据库事 务隔离级别的不同，可能修改数据库需要conn.commit
4. 关闭cur, conn

参考文档：http://anony3721.blog.163.com/blog/static/5119742010716104442536/
         https://www.pythoncentral.io/introduction-to-sqlite-in-python/
'''

import sqlite3

class SQLite3Util:
    def __init__(self, dbfile=None):
        if self.dbfile is None:
            self.db = sqlite3.connect(':memory:')
        else:
            self.db = sqlite3.connect(dbfile)

        self.c = self.db.cursor()

    def query(self, sql, param=None):
        """
        查询语句
        sql：sql语句
        param：参数,可为None
        retutn：成功返回True
        """
        if param is None:
            self.c.execute(sql)
        else:
            self.c.execute(sql,param)
        return self.c.fetchall()

    def execute(self, sql, param=None):
        """
            param：数据，可以是list或tuple，亦可是None
          
            在python中，使用sqlite3创建数据库的连接，当我们指定的数据库文件不存在的时候
            连接对象会自动创建数据库文件；如果数据库文件已经存在，则连接对象不会再创建
            数据库文件，而是直接打开该数据库文件。

            execute()           --执行一条sql语句

            executemany()       --执行多条sql语句

            fetchone()                               --从结果中取出一条记录

            fetchmany(size=cursor.arraysize)         --从结果中取出多条记录

            fetchall()                               --从结果中取出所有记录

            参考文档：https://www.pythoncentral.io/introduction-to-sqlite-in-python/


            例子： 创建表
            sql_lang = '''CREATE TABLE IF NOT EXISTS users (
                            id             INTEGER    PRIMARY KEY autoincrement,
                            username       TEXT       unique NOT NULL,
                            name           TEXT       NOT NULL,
                            password       TEXT       NOT NULL,
                            email          TEXT       NOT NULL,
                            date           TIMESTAMP  DEFAULT CURRENT_TIMESTAMP NOT NULL
                        );
       """ 
        # We use the function sqlite3.connect to connect to the database.
        # We can use the argument ":memory:" to create a temporary DB in the RAM or pass the name of a file to open or create it.


        try:
            if param is None:
                self.c.execute(sql)
            else:
                if isinstance(sql, list):
                    self.c.executemany(sql,param)
                else :
                    self.c.execute(sql,param)
            count = self.db.total_changes
            self.db.commit()
        except (sqlite3.IntegrityError, sqlite3.DatabaseError, sqlite3.OperationalError) as e:
            raise e
        
        if count > 0 :
            return True
        else :
            return False


    def close(self):
        """
        关闭数据库
        """
        self.c.close()
        self.db.close()

