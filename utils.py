# 短信发送SDK
from tencentcloud.sms.v20190711 import sms_client, models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common import credential
# END

import datetime
import json
import hashlib

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