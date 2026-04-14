import sqlite3
import pathlib

class HistoryDataBase:
    def __init__(self, database_path):
        self.database_path = database_path
        self.init_database()


    def init_database(self):
        """
        初始化数据库表结构
        如果数据库文件已存在，则直接返回
        如果不存在，则创建新的数据库表
        """
        if pathlib.Path(self.database_path).exists(): return  # 检查数据库文件是否存在，存在则直接返回

        db = sqlite3.connect(self.database_path)
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE results 
            (
                时间 TEXT,
                文件 TEXT,
                缺陷类型 TEXT,
                置信度 REAL,
                Xmin INTEGER,
                Xmax INTEGER,
                Ymin INTEGER,
                Ymax INTEGER
            )
        ''')
        db.commit()
        cursor.close()
        db.close()

    def insert_data(self, data):
        db = sqlite3.connect(self.database_path)
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            data
        )
        db.commit()
        cursor.close()
        db.close()

history_db = HistoryDataBase("history.db")
