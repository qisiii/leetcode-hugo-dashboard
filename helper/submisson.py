import os
import sqlite3
import requests
from .config import config
from .login import Login
from .utils import handle_tasks,convert_cookies_to_dict
from .node import InfoNode, ProblemInfoNode, ProblemDescNode, SubmissionNode
from .constants import PROBLEMS, HEADERS, GRAPHQL, CODE_FORMAT



class Submisson:
    def __init__(self,type='default'):
        self.type=type
        self.login = Login(config.username, config.password,config.cookies)
        self.__db_dir = os.path.abspath(os.path.join(__file__, "../..", "db"))
        if not os.path.exists(self.__db_dir):
            os.makedirs(self.__db_dir)
        self.db_path = os.path.join(self.__db_dir, "test.db" if type=='test' else "hugo.db")
        self.__cookies = convert_cookies_to_dict(self.login.cookies)
        
    
    def getSql(self):
        if self.type=='test':
            return "select 'two-sum';"
        elif self.type=='rebuild':
            return "SELECT title_slug FROM problem WHERE status == 'ac'"
        else:
            return "SELECT p.title_slug FROM problem p left join submission s on s.title_slug=p.title_slug WHERE status == 'ac' and s_stored==0"
    
    def update(self):
        self.storeSubmissions()
        self.storeCodes()

    def updateSubmissions(self,type=1):
        '''更新处理后的 submission 数据库'''
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE submission SET s_stored={}'.format(type))
        conn.commit()
        conn.close()

    def storeSubmissions(self):
        '''存储提交的代码信息'''
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS submission (
                submission_id INTEGER,
                lang TEXT,
                language TEXT,
                memory TEXT,
                runtime TEXT,
                timestamp TEXT,
                title_slug TEXT,
                comment TEXT,
                flag TEXT,
                s_stored INTEGER DEFAULT 0,
                PRIMARY KEY(submission_id)
            )
            ''')
        c.execute(self.getSql())
        res = c.fetchall()
        if not res:
            return
        ll=[dict(title_slug=t[0]) for t in res]
        submissions_list=[]
        for t in ll:
            submissions_list.append(self.getSubmissionList(t['title_slug']))
        data = []
        for submissions, title_slug in submissions_list:
            for submission in submissions['data']['submissionList'][
                    'submissions']:
                submission['title_slug']=title_slug
                data.append(submission)
        for submission in data:
            try:
                s = SubmissionNode(submission)
                c.execute(
                    '''
                    INSERT OR IGNORE INTO submission (
                        submission_id, lang, language, memory, runtime, timestamp, title_slug,comment,flag
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    ''', (s.submission_id, s.lang, s.language, s.memory, s.runtime,
                        s.timestamp, s.title_slug,s.comment,s.flag))
            except Exception as e:
                print('{}出现异常,实体为{}'.format(submission['title_slug'],submission),e)
        conn.commit()
        conn.close()

    def storeCodes(self):
        '''存储提交的代码'''
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT s.submission_id FROM submission s where s_stored=0  or code isnull"
        )
        res = c.fetchall()
        if not res:
            return
        ll=[dict(submission_id=t[0]) for t in res]
        codes_list=[]
        for t in ll:
            codes_list.append(self.getCode(t['submission_id']))
        try:
            c.execute("ALTER TABLE submission ADD COLUMN code TEXT")
        except sqlite3.OperationalError:
            pass
        for code,submission_id in codes_list:
            try:
                c.execute(
                    """
                    UPDATE submission SET code = ?
                    WHERE submission_id = ?
                    """, (code['data']['submissionDetail']['code'],submission_id))
            except Exception as e:
                print('存储id为{}的code时异常,实体为{}'.format(submission_id,code),e)
        conn.commit()
        conn.close()

    def getSubmissionList(self, title_slug, offset=0, limit=5):
        print('获取{}提交记录'.format(title_slug))
        payload = {
            'query': '''
            query submissionList(
            $offset: Int!
            $limit: Int!
            $questionSlug: String!
            $status: SubmissionStatusEnum
            ) {
            submissionList(
                offset: $offset
                limit: $limit
                questionSlug: $questionSlug
                status: $status
            ) {
                lastKey
                hasNext
                submissions {
                id
                title
                status
                statusDisplay
                lang
                langName: langVerboseName
                runtime
                timestamp
                url
                isPending
                memory
                submissionComment {
                    comment
                    flagType
                }
                }
            }
            }
            ''',
            'operationName': 'submissionList',
            'variables': {
                'limit': limit,
                'offset': offset,
                'questionSlug': title_slug,
                'status': 'AC'
            }
        }
        resp = requests.post(GRAPHQL,json=payload,headers=HEADERS,cookies=self.__cookies)
        return resp.json(), title_slug
    
    def getCode(self, submission_id):
        print('获取Id为{}提交记录的代码'.format(submission_id))
        payload = {
            'query': '''
            query submissionCode($submissionId: ID!) {
                submissionDetail(submissionId: $submissionId) {
                    code
                }
            }
            ''',
            'operationName': 'submissionCode',
            'variables': {
                'submissionId': submission_id
            }
        }
        resp = requests.post(GRAPHQL,json=payload,headers=HEADERS,cookies=self.__cookies)
        return resp.json(),submission_id
