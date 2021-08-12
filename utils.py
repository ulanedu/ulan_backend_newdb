# 短信发送SDK
from tencentcloud.sms.v20190711 import sms_client, models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common import credential
# END

import hashlib
import time
import datetime
import json
import requests
import pickle

def getTimestamp():
    return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def getPersonalCoursePayStatus(courseId):

    isPay = False

    from conf.conn import getCursor
    with getCursor() as cs:
        sql = '''
        SELECT MAX(`orders`.`status`)
        FROM `order_goods`
        LEFT JOIN `orders` ON `orders`.id = `order_goods`.oid
        WHERE `order_goods`.goods_type = 'COURSE' AND `order_goods`.goods_id = %s
        '''
        cs.execute(sql, courseId)
        res = cs.fetchone()[0]

        if (res == 9):
            isPay = True

    return isPay


def sendVerifyMessage(mobile):
    import random
    code = random.randint(100000, 999999)

    try:
        cred = credential.Credential(
            "AKIDzqwpmcmdmDNH4sv69vd2FCze29znBc1W", "NVQEsGNylMhrsc5HC8qGSVHly6G7h14q")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "sms.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = sms_client.SmsClient(cred, "", clientProfile)

        req = models.SendSmsRequest()
        params = {
            "PhoneNumberSet": ["86{}".format(mobile)],
            "TemplateParamSet": ["{}".format(code)],
            "TemplateID": "648669",
            "SmsSdkAppid": "1400347804",
            "Sign": "优兰辅导"
        }
        req.from_json_string(json.dumps(params))

        resp = client.SendSms(req)
        print(resp.to_json_string())

        return code
    except TencentCloudSDKException as err:
        print(err)
        return -1


def getNumOfPersonalCourseCandidates(courseId):
    teacherNum = -1

    from conf.conn import getCursor
    with getCursor() as cs:
        sql = '''
        SELECT COUNT(id)
        FROM `course_teacher_mapping`
        WHERE courseId = %s
        '''
        cs.execute(sql, int(courseId))
        res = cs.fetchone()
        print(res)
        if (res):
            teacherNum = res

    return teacherNum


def genMD5(str):
    h1 = hashlib.md5()
    h1.update(str.encode(encoding='utf-8'))

    return h1.hexdigest()


def directGetAccessToken():
    url_access_token = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx740eff9eb1f79506&secret=4c875175aac4af592a7d82a130765906'
    tokenRes = requests.get(url_access_token)
    token = json.loads(tokenRes.text).get('access_token')
    return token


def getAccessToken():
    try:
        with open('access_token.pkl','rb') as file:
            data = pickle.load(file)
        if data & (time.time() - data['expires_in']) < 7100:
            token = data['token']
            return token
        else:
            token = directGetAccessToken()
            dic = {'token':token,'expires_in':time.time()}
            with open('access_token.pkl','wb') as file:
                pickle.dump(dic,file)
            return token
    except:
        token = directGetAccessToken()
        dic = {'token':token,'expires_in':time.time()}
        with open('access_token.pkl','wb') as file:
            pickle.dump(dic,file)
        return token


def send(openId, name, msg):
    print('openId:', openId)
    print(msg)
    if len(msg) > 20:
        msg = msg[:20]
    try:
        token = getAccessToken()
        url_msg = 'https://api.weixin.qq.com/cgi-bin/message/subscribe/send'
        body = {
            "touser": openId,  # 也就是OPENID
            "template_id": "1k9t9ca1H5vedby9WpEA0Pl5noxq40ZPUEI7QhDQjYQ",
            "page": "pages/index/index",
            "data": {
                "thing1": {
                    "value": name
                },
                "thing2": {
                    "value": msg
                }
            }
        }

        res = requests.post(url=url_msg, params={
            'access_token': token  # 这里是我们上面获取到的token
        }, data=json.dumps(body, ensure_ascii=False).encode('utf-8'))
        print(1)
        print(type(res.text))
        # {"errcode":0,"errmsg":"ok"}
        print(res.text)
        if json.loads(res.text)['errcode'] == 0:
            print('success')
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

if __name__ == '__main__':
    send('oEtjz5AqOql3zdhg7Cx4SjcJON6Q','1','2')


