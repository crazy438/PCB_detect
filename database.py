import sqlite3
from shared_data import shared_data

class Database:
    def __init__(self, database_path = shared_data.database_path):
        self.database_path = database_path

    def __enter__(self):
        self.db = sqlite3.connect(self.database_path)
        self.cursor = self.db.cursor()
        self.cursor.execute('PRAGMA foreign_keys = ON') # 开启外键约束
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.db.rollback() # 有异常则回滚数据库
            else:
                self.db.commit()
        finally:
            self.cursor.close()
            self.db.close()

        return False # 返回 False 表示不抑制异常，让异常继续向外传播

    def init_table(self):
        # 图片文件表
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS imgs 
            (
                timestamp INTEGER PRIMARY KEY AUTOINCREMENT,
                img_path TEXT NOT NULL,
                model TEXT NOT NULL
            )
        ''')

        # 缺陷类型
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS defects 
            (
                defect_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                defect_type TEXT NOT NULL,
                conf REAL NOT NULL,
                Xmin INTEGER NOT NULL,
                Xmax INTEGER NOT NULL,
                Ymin INTEGER NOT NULL,
                Ymax INTEGER NOT NULL,
                FOREIGN KEY (timestamp) REFERENCES imgs(timestamp) ON DELETE CASCADE,
                CHECK (conf BETWEEN 0 AND 1),
                CHECK (xmin < xmax AND ymin < ymax)
            )
        ''')

        # 新增索引：加速常用查询
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_img_path ON imgs(img_path)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON defects(timestamp)')

    def imgs_insert(self, data):
        self.cursor.executemany(
            f"""
            INSERT INTO imgs (timestamp, img_path, model)
            VALUES (?, ?, ?)
            """,
            data
        )

    def defects_insert(self, data):
        self.cursor.executemany(
            f"""
            INSERT INTO defects (timestamp, defect_type, conf, Xmin, Xmax, Ymin, Ymax)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            data
        )

    def defects_query(self, timestamps = None):
        if timestamps:
            self.cursor.execute(
                f"""
                SELECT defect_type, conf, Xmin, Xmax, Ymin, Ymax FROM defects WHERE timestamp IN ({','.join(['?']*len(timestamps))})
                """,
                timestamps
            )
        else:
            self.cursor.execute(
                f"""
                SELECT timestamp, defect_type, conf, Xmin, Xmax, Ymin, Ymax FROM defects
                """
            )
        return self.cursor.fetchall()

    # 统计每类缺陷的数量
    def defects_statistics_query(self, timestamps = None):
        if timestamps:
            self.cursor.execute(
                f"""
                SELECT defect_type, COUNT(*) AS count
                FROM defects
                WHERE timestamp IN ({','.join(['?']*len(timestamps))})
                GROUP BY defect_type
                """,
                timestamps
            )
        else:
            self.cursor.execute(
                f"""
                SELECT defect_type, COUNT(*) AS count
                FROM defects
                GROUP BY defect_type
                """
            )
        return self.cursor.fetchall()

    # 统计每张图片的缺陷数量
    def defects_count_query(self, timestamps = None):
        if timestamps:
            self.cursor.execute(
                f"""
                SELECT defect_type, COUNT(*) AS count
                FROM defects
                WHERE timestamp IN ({','.join(['?']*len(timestamps))})
                GROUP BY defect_type
                """
            )
        else:
            self.cursor.execute(
                f"""
                SELECT defect_type, COUNT(*) AS count
                FROM defects
                GROUP BY defect_type
                """
            )
        return self.cursor.fetchall()

    def imgs_query(self, timestamps = None):
        if timestamps:
            self.cursor.execute(
                f"""
                SELECT imgs.timestamp, imgs.img_path, imgs.model, COUNT(defects.defect_id) AS defect_count
                FROM imgs
                LEFT JOIN defects ON imgs.timestamp = defects.timestamp
                WHERE imgs.timestamp = ?
                GROUP BY imgs.timestamp
                """,
                timestamps
            )
        else:
            self.cursor.execute(
                f"""
                SELECT 
                    imgs.timestamp, 
                    imgs.img_path, 
                    imgs.model, 
                    COUNT(defects.defect_id) AS defect_count
                FROM imgs
                LEFT JOIN defects ON imgs.timestamp = defects.timestamp
                GROUP BY imgs.timestamp
                """
            )
        return self.cursor.fetchall()

    def delete_rows(self, timestamps):
        # 只删除主表 imgs，从表 defects 自动级联删除
        self.cursor.execute(
            f"DELETE FROM imgs WHERE timestamp IN ({','.join(['?']*len(timestamps))})",
            timestamps
        )

    def clear(self):
        self.cursor.execute(f"DELETE FROM imgs")

if __name__ == "__main__":
    data = [(1776494273725, 'C:\\Users\\27843\\Desktop\\detection_platform\\output\\2026年04月18日00-36-18-181964\\01_missing_hole_04.jpg', "YOLO26"), (1776494273726, 'C:\\Users\\27843\\Desktop\\detection_platform\\output\\2026年04月18日00-36-18-181964\\01_spur_10.jpg', "YOLO26")]
    with Database() as db:
        # db.init_table()
        # db.imgs_insert(data)
        # db.defects_insert([(1776494273725, "hole", 0.9, 0, 100, 0, 100), (1776494273725, "spur", 0.8, 0, 100, 0, 100),(1776494273726, "hole", 0.9, 0, 100, 0, 100), (1776494273726, "spur", 0.8, 0, 100, 0, 100)])
        t = db.defects_statistics_query([1776529371373, 1776497832049])
        print(t)