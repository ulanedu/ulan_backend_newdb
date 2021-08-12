import flask
import redis
from utils import *
from conf.conf import *
from conf.conn import getCursor


wx_co = flask.Blueprint("wx_co", __name__)


@wx_co.route('/api/w_v1/co/getCaptcha', methods=['POST'])
def getCaptcha():
    data = flask.request.get_json()
    code = sendVerifyMessage(data['phone_number'])
    if (code != -1):
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.set(data['phone_number'], code, ex=15*60*1000)  # 验证码有效期15分钟
        return 'success'
    else:
        return 'failed', 400


@wx_co.route('/api/w_v1/co/getPersonalCourseRecords/<int:courseId>', methods=['GET'])
def getPersonalCourseRecords(courseId):

    ret = {
        'code': -1,
        'msg': '',
        'data': []
    }

    statusMapping = ['待审核', '审核通过', '审核未通过']

    with getCursor() as cs:
        sql1 = '''
        SELECT
            course_personal_records.id,
            course_personal_records.title,
            course_personal_records.hours,
            course_personal_records.record,
            course_personal_records.created_at,
            course_personal_records.updated_at,
            course_personal_records.status
        FROM
            course_personal_records
        WHERE course_personal_records.courseId = %s
        '''
        try:
            cs.execute(sql1, int(courseId))
            data = cs.fetchall()
            for item in data:
                nowItem = {}

                nowItem['hours'] = item[2]
                nowItem['statusText'] = statusMapping[item[6]]
                nowItem['title'] = item[1]
                nowItem['record'] = item[3]
                # nowItem['body'] = '课时主题\n{}\n课时记录\n{}\n'.format(
                #     item[1], item[3])
                nowItem['created_at'] = str(item[4])
                nowItem['updated_at'] = str(item[5])
                nowItem['open'] = False
                ret['data'].append(nowItem)

            ret['code'] = 0
            ret['msg'] = '评论成功'
        except Exception as e:
            ret['msg'] = str(e)

    return makeRespose(ret)
