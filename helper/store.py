import os
import sqlite3
import shutil
from .config import config
from .extractor import Extractor
from .problem import Problem
from .submisson import Submisson

class Store:
    def __init__(self,type='default'):
        self.type=type
        self.__db_dir = os.path.abspath(os.path.join(__file__, "../..", "db"))
        if not os.path.exists(self.__db_dir):
            os.makedirs(self.__db_dir)
        self.db_path = os.path.join(self.__db_dir, "test.db" if type=='test' else "hugo.db")
        self.problem=Problem(self.type)
        self.submisson=Submisson(self.type)

    def __dict_factory(self, cursor, row):
        '''修改 SQLite 数据呈现方式'''
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def store(self):
            output_dir = config.outputDir
            if(self.type=='test'):
                output_dir = os.path.abspath(os.path.join(__file__, "../../content", "store"))
            if(self.type=='rewrite' or self.type=='test'):
                self.del_file(output_dir)
                self.problem.updateProblemsDesc(0)
                self.submisson.updateSubmissions(0)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            extractor = Extractor(output_dir, config.username)
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = self.__dict_factory
            c = conn.cursor()
            # 获取新的数据
            c.execute('''
                SELECT *
                FROM description d
                JOIN problem p
                ON p.id=d.id
                JOIN submission s
                ON p.title_slug=s.title_slug
                WHERE (d.d_stored=0 OR s.s_stored=0)
                ORDER BY p.id DESC
                ''')
            datas = c.fetchall()
            if datas:
                extractor.extractDesc(datas)
                self.problem.updateProblemsDesc()
                extractor.extractCode(datas)
                self.submisson.updateSubmissions()
            c.execute('''
                SELECT *
                FROM description d
                JOIN problem p
                ON p.id=d.id
                JOIN submission s
                ON p.title_slug=s.title_slug
                ORDER BY timestamp DESC
                ''')
            datas = c.fetchall()
            extractor.extractInfo(self.problem.info, datas)
            print('数据已更新！')
            conn.close()

    def clearDB(self):
        '''重建数据'''
        print('--开始清除数据库--')
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT name
            FROM sqlite_master
            WHERE type="table" AND name="problem"
            ''')
        if c.fetchone():
            # 删除 problem 表
            c.execute('DROP TABLE problem')
        c.execute('''
            SELECT name
            FROM sqlite_master
            WHERE type="table" AND name="description"
            ''')
        if c.fetchone():
            # 删除 description 表
            c.execute('DROP TABLE description')
        c.execute('''
            SELECT name
            FROM sqlite_master
            WHERE type="table" AND name="submission"
            ''')
        if c.fetchone():
            # 删除 submission 表
            c.execute('DROP TABLE submission')
        conn.commit()
        conn.close()
        print('--结束清除数据库--')
    
    def del_file(self,path):
      if not os.listdir(path):
            print('目录为空！')
      else:
        for i in os.listdir(path):
            path_file = os.path.join(path,i)  #取文件绝对路径
            print(path_file)
            if os.path.isfile(path_file):
                os.remove(path_file)
            else:
                self.del_file(path_file)
