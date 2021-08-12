from conf.conf import *
from conf.conn import getCursor
import requests
import json


def getStudentIdByopenid(openid):
    user_id = -1
    with getCursor() as cs:
        sql = 'SELECT user_id FROM socialite WHERE app_user_id = %s'
        cs.execute(sql, openid)
        res = cs.fetchone()
        print(res)
        if(res):
            user_id = res[0]
        else:
            pass
    return int(user_id)


def getTeacherBaseInfoByopenid(openid):
    re  =  (-1, -1)
    with getCursor() as cs:
        sql = 'SELECT uid,teacher_status FROM `teacher` WHERE wechat_openid=%s'
        cs.execute(sql, openid)
        data = cs.fetchone()
        if (data):
            re = (data[0],data[1])
    
    return re


def getUserOpenId(code):
    # 后期改成从数据库获取
    appid = 'wx6fb6fd535110d855'
    secret = '8c4a58840ed3e5a47de16da196edeb26'
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'.format(
        appid, secret, code
    )

    data = json.loads(requests.get(url).text)
    print(data)
    if (data.get('errcode', 0) == 0):
        return data['openid']
    else:
        return - 1
        
        