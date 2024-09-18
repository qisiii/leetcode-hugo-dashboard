import sqlite3
import aiohttp
import requests
# LeetCode 相关链接
LEETCODE = "https://leetcode.cn"
GRAPHQL = LEETCODE + "/graphql"
LOGIN = "https://leetcode-cn.com/accounts/login/"
PROBLEMS = LEETCODE + "/api/problems/all/"
SUBMISSIONS_FORMAT = LEETCODE + "/api/submissions/?offset={}&limit=20"
CODE_FORMAT = LEETCODE + "/submissions/latest/?qid={}&lang={}"
TAG_FORMAT = LEETCODE + "/tag/{}"
PROBLEM_FORMAT = LEETCODE + "/problems/{}/"
cookie="gr_user_id=9f5d2a6c-ef0a-4d28-88bc-85a83f345a53; _bl_uid=RmlpszzFsvv26vvC4d199t6its1k; _gid=GA1.2.26547175.1726037751; aliyungf_tc=b770a109d904cbbe21c9f4e651521ee60a7b6bf780b9ab9f43d5f4d459571b98; Hm_lvt_f0faad39bcf8471e3ab3ef70125152c3=1726037751,1726140001,1726214691,1726472256; HMACCOUNT=30421E1284B66711; Hm_lvt_fa218a3ff7179639febdb15e372f411c=1726485754; Hm_lpvt_fa218a3ff7179639febdb15e372f411c=1726486072; a2873925c34ecbd2_gr_last_sent_cs1=qisiii; messages=.eJyLjlaKj88qzs-Lz00tLk5MT1XSMdAxMtVRiik1M0i0iCk1TUkziik1T01OA5Jm5klAEcO0RKVYnRGgMRYAVShbLQ:1sqGUD:mqMVH06B6Z7LEacXvSQCs_TNErl3G5U3mDq2C3hTNF0; csrftoken=yAOXyoyqXBrn91nZpcEEhTxaVx2yMdMUIOtANgGZIzy45ucjnFsPnJuHfAMkWifN; tfstk=fuJjCZZM-FprtCGqOlnPNukEL5Ws4FMElls9xhe4XtBxfRTevK7qSmA55U_omKuc3Rd6xhbAQtJqCC_RH1AV7Z71ChYI42kELnxcIt3E8vlw179GK5FTBPW8wMab4Y0tLnx02T7YCLHU1xalWCQ9WsCRwGb8MoLTHYn5XGzY6-LtV3QlcieAW-QJ2GIOBNLOk0_RxUuzhgofrniRVyhLkf3X0awTpkjVM4t4_JyUpiflvGWuBi95cs_pDKxD45S69p1DJ4PVkBOwRM8qe-TBDEOd9KU-POxyOFsBHDFC5ExJ3_pxbWjlIIddHdgQk3CBeKWDN2wFJQx9C_KmRWjy6HJ21EuuBZRB2U1eUzyFeKTXH_6d4CeFR1Kb1u13Cg_EV0Ngsb_9o4dzWoSNMgjr70i7ThfAqgO-V0NgssIl4anSVW-G.; __appToken__=; LEETCODE_SESSION=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfYXV0aF91c2VyX2lkIjoiMzYxNyIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImFsbGF1dGguYWNjb3VudC5hdXRoX2JhY2tlbmRzLkF1dGhlbnRpY2F0aW9uQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImYzY2NmYjViOTE0N2Y1ZWI4OTU4MDZkYjE5NmNjZGJjMWViNGU4MmUzYTk5N2RiODQ3NzliZTg4OTEzZTUxM2QiLCJpZCI6MzYxNywiZW1haWwiOiJoa2M4MTAyMTVAMTYzLmNvbSIsInVzZXJuYW1lIjoicWlzaWlpIiwidXNlcl9zbHVnIjoicWlzaWlpIiwiYXZhdGFyIjoiaHR0cHM6Ly9hc3NldHMubGVldGNvZGUuY24vYWxpeXVuLWxjLXVwbG9hZC91c2Vycy91c2VyMDY1NS9hdmF0YXJfMTcyNjQ4NTg4Ny5wbmciLCJwaG9uZV92ZXJpZmllZCI6dHJ1ZSwiZGV2aWNlX2lkIjoiYTg1ODliOTlmMjMyMzM2OTEwNWQyYjA2NmRlMjI3ZGIiLCJpcCI6IjExMS4xOTQuMTIzLjc1IiwiX3RpbWVzdGFtcCI6MTcyNjU0MDgzMi42NDIyMTg4LCJleHBpcmVkX3RpbWVfIjoxNzI5MTA1MjAwLCJ2ZXJzaW9uX2tleV8iOjIsImxhdGVzdF90aW1lc3RhbXBfIjoxNzI2NTQzNzY1fQ.E0MIq0l8uiEaM1ixa1EJJTgSX1KhufsNGpdgbUIPt4U; _ga_PDVPZYN3CW=GS1.1.1726548621.32.1.1726551287.16.0.0; sl-session=oi0UETmc62b0kB3ksSY6MQ==; a2873925c34ecbd2_gr_session_id=34f0fff5-c56a-47b5-8e22-c1a426586393; a2873925c34ecbd2_gr_last_sent_sid_with_cs1=34f0fff5-c56a-47b5-8e22-c1a426586393; a2873925c34ecbd2_gr_cs1=qisiii; Hm_lpvt_f0faad39bcf8471e3ab3ef70125152c3=1726649781; a2873925c34ecbd2_gr_session_id_sent_vst=34f0fff5-c56a-47b5-8e22-c1a426586393; _gat=1; _ga=GA1.1.2067809652.1723532699; _ga_PDVPZYN3CW=GS1.1.1726649781.35.0.1726649791.50.0.0"

HEADERS = {
    'Origin':
    LEETCODE,
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
}
def getproblem():
    resp = requests.get(PROBLEMS, headers=HEADERS,cookies=convert_cookies_to_dict(cookie))
    print(resp.json())

def getDesc():
    conn = sqlite3.connect("/Users/hkc/Research/hugo-leetcode-dashboard/hugo-leetcode-dashboard/db/leetcode.db")
    c = conn.cursor()
    c.execute("SELECT title_slug FROM problem WHERE status == 'ac' limit 2")
    res = c.fetchall()
    if not res:
        return
    ll=[dict(title_slug=t[0]) for t in res]
    for t in ll:
        # getProblemDesc(t['title_slug'])
        __getSubmissions(t['title_slug'])
    conn.close()

def getProblemDesc(title_slug):
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
        res = requests.post(GRAPHQL,json=payload,headers=HEADERS,cookies=convert_cookies_to_dict(cookie))
        print(res.json())
        return res.json()

def __getSubmissions(title_slug, offset=0, limit=500):
    payload = {
        'query': '''
        query submissions($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
            submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
                lastKey
                hasNext
                submissions {
                    id
                    statusDisplay
                    lang
                    runtime
                    timestamp
                    url
                    isPending
                    memory
                    __typename
                }
            __typename
            }
        }
        ''',
        'operationName': 'submissions',
        'variables': {
            'limit': limit,
            'offset': offset,
            'questionSlug': title_slug
        }
    }
    res = requests.post(GRAPHQL,json=payload,headers=HEADERS,cookies=convert_cookies_to_dict(cookie))
    return res.json(),title_slug

def storeCodes():
    '''存储提交的代码'''
    conn = sqlite3.connect("/Users/hkc/Research/hugo-leetcode-dashboard/hugo-leetcode-dashboard/db/leetcode.db")
    c = conn.cursor()
    c.execute(
        "SELECT p.id, lang FROM submission s LEFT JOIN problem p ON s.title_slug=p.title_slug limit 1"
    )
    res = c.fetchall()
    if not res:
        return
    ll=[dict(qid=t[0], lang=t[1])  for t in res]
    codes_list=[]
    for t in ll:
        print(t['qid'])
        print(t['lang'])
        getCode(t['qid'],t['lang'])

def getCode(qid, lang):
    url = CODE_FORMAT.format(qid, lang)
    resp = requests.get(url,headers=HEADERS,cookies=convert_cookies_to_dict(cookie))
    return  resp.json(), qid, lang           
 
def convert_cookies_to_dict(cookies):
    cookies = dict([l.split("=", 1) for l in cookies.split("; ")])
    return cookies
def path():
    output_dir="/Users/hkc/resource/hugo/content/leetcode"
    print()

# getDesc()
# getproblem()
# print(__getSubmissions('two-sum'))
# storeCodes()
path()