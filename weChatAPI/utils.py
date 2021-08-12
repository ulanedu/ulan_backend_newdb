from redis import DataError
from conf.conf import *
from conf.conn import getCursor
import requests
import json

# 通过用户openid查询用户id
def getUserIdByopenid(openid):

    with getCursor() as cs:
        sql = '''
        SELECT User_Id FROM tbl_User WHERE User_OpenId = {}
        '''.format(openid)
        cs.execute(sql)
        data = cs.fetchone()
        if(data):
            return int(data[0])
        else:
            return 0


def getTeacherIdByopenid(openid):

    with getCursor() as cs:
        sql = '''
        SELECT Teac_Id FROM tbl_Teacher WHERE Teac_OpenId = {}
        '''.format(openid)
        cs.execute(sql)
        data = cs.fetchone()
        if (data):
            return int(data[0])
        else:
            return 0


def getUserOpenId(code):
    # 后期改成从数据库获取
    appid = 'wx6fb6fd535110d855'
    secret = '8c4a58840ed3e5a47de16da196edeb26'
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'.format(
        appid, secret, code
    )

    data = json.loads(requests.get(url).text)
    if (data.get('errcode', 0) == 0):
        return data['openid']
    else:
        return - 1