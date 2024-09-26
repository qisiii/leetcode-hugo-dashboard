import os
import sqlite3
import requests
from .config import config
from .login import Login
from .utils import convert_cookies_to_dict
from .node import InfoNode, ProblemInfoNode, ProblemDescNode
from .constants import PROBLEMS, HEADERS, GRAPHQL


class Problem:
    '''核心逻辑'''
    def __init__(self,type='default'):
        self.type=type
        self.login = Login(config.username, config.password,config.cookies)
        self.__db_dir = os.path.abspath(os.path.join(__file__, "../..", "db"))
        if not os.path.exists(self.__db_dir):
            os.makedirs(self.__db_dir)
        self.db_path = os.path.join(self.__db_dir, "test.db" if type=='test' else "hugo.db")
        self.__cookies = convert_cookies_to_dict(self.login.cookies)
        self.problems_json = self.__getProblemsJson()


    def __getProblemsJson(self):
        resp = requests.get(PROBLEMS, headers=HEADERS, cookies=self.__cookies)
        if resp.status_code == 200:
            return resp.json()

    @property
    def info(self):
        '''获取用户基本信息'''
        return InfoNode(self.problems_json)
    
    def getSql(self):
        if self.type=='test':
            return "select 'two-sum';"
        elif self.type=='rebuild':
            return "SELECT title_slug FROM problem WHERE status == 'ac'"
        else:
            return "select p.title_slug from problem p left join description d on p.id = d.id where p.status='ac' and  d.content_cn isnull"
            

    def updateProblemsInfo(self):
        '''更新问题基本信息'''
        problems_list = self.problems_json.get('stat_status_pairs')
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS problem (
                id INTEGER,
                frontend_id TEXT,
                title_en TEXT,
                title_slug TEXT ,
                difficulty INTEGER,
                paid_only INTEGER,
                is_favor INTEGER,
                status TEXT,
                total_acs INTEGER,
                total_submitted INTEGER,
                ac_rate TEXT,
                PRIMARY KEY(id)
            )
            ''')
        c.execute('DELETE FROM problem')
        for problem in problems_list:
            p = ProblemInfoNode(problem)
            c.execute(
                '''
                INSERT OR REPLACE INTO problem (
                    id, frontend_id, title_en, title_slug, difficulty, paid_only, is_favor, status, total_acs, total_submitted, ac_rate
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                ''', (p.id, p.frontend_id, p.title_en, p.title_slug,
                      p.difficulty, p.paid_only, p.is_favor, p.status,
                      p.total_acs, p.total_submitted, p.ac_rate))
        conn.commit()
        conn.close()

    def getProblemDesc(self,title_slug):
        print('获取{}的问题描述'.format(title_slug))
        payload = {
            'query': '''
            query questionData($titleSlug: String!) {
                question(titleSlug: $titleSlug) {
                    questionId
                    content
                    translatedTitle
                    translatedContent
                    similarQuestions
                    topicTags {
                        name
                        slug
                        translatedName
                    }
                    hints
                }
            }
            ''',
            'operationName': 'questionData',
            'variables': {
                'titleSlug': title_slug
            }
        }
        res = requests.post(GRAPHQL,json=payload,headers=HEADERS,cookies=self.__cookies)
        return res.json(),title_slug

    

    def storeProblemsDesc(self):
        '''存储 AC 问题描述信息'''
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS description (
                id INTEGER,
                title_slug TEXT ,
                content_en TEXT,
                title_cn TEXT,
                content_cn TEXT,
                similar_questions_cn TEXT,
                similar_questions_en TEXT,
                tags_cn TEXT,
                tags_en TEXT,
                d_stored INTEGER DEFAULT 0,
                PRIMARY KEY(id)
            )
            ''')
        c.execute(self.getSql())
        res = c.fetchall()
        if not res:
            return
        ll=[dict(title_slug=t[0]) for t in res]
        problems_list=[]
        for t in ll:
            problems_list.append(self.getProblemDesc(t['title_slug']))

        for problem,title_slug in problems_list:
            p = ProblemDescNode(problem)
            c.execute(
                '''
                INSERT OR IGNORE INTO description (
                    id,title_slug, content_en, title_cn, content_cn, similar_questions_cn, similar_questions_en, tags_cn, tags_en
                )
                VALUES (
                    ?, ? ,?, ?, ?, ?, ?, ?, ?
                )
                ''', (p.id,title_slug, p.content_en, p.title_cn, p.content_cn,
                      p.similar_questions_cn, p.similar_questions_en,
                      p.tags_cn, p.tags_en))
        conn.commit()
        conn.close()

    def updateProblemsDesc(self,value=1):
        '''更新处理后的 description 数据库'''
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE description SET d_stored={}'.format(value))
        conn.commit()
        conn.close()

    def update(self):
        self.updateProblemsInfo()
        self.storeProblemsDesc()