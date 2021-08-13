import flask
import redis
from utils import *
from conf.conf import *
from conf.conn import getCursor


wx_common = flask.Blueprint("wx_common", __name__)


@wx_common.route('/api/weChat/common/getCaptcha', methods=['POST'])
def getCaptcha():
    #获取验证
    data = flask.request.get_json()
    code = sendVerifyMessage(data['phone_number'])
    if (code != -1):
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.set(data['phone_number'], code, ex=15*60*1000)  # 验证码有效期15分钟
        # r.set('food', 'mutton', ex=3)
        # key是"food" value是"mutton" 将键值对存入redis缓存
        #ex - 过期时间（秒）
        #decode_responses=True:这样写存的数据是字符串格式
        return 'success'
    else:
        return 'failed', 400


@wx_common.route('/api/weChat/common/getPersonalCourseRecords/<int:courseId>', methods=['GET'])
def getPersonalCourseRecords(courseId):
    ret = {
        'code': -1,
        'msg': '',
        'data': []
    }
    statusMapping = ['待审核', '审核通过', '审核未通过']

    with getCursor() as cs:
        sql = '''
            SELECT
                DiAp_Id,
                DiAp_CourseContent,
                DiAp_DismissedHour,
                DiAp_UserEvaluation,
                DiAp_ApplicationTime,
                DiAp_AdminReviewTime,
                DiAp_UserReviewStatus
            FROM
                tbl_DismissalApplication
            WHERE DiAp_CourseId = {}
            '''.format(courseId)
        try:
            cs.execute(sql)
            data = cs.fetchall()
            dataKeys = {'daid', 'courseContent', 'dismissedHour', 'userEvaluation', 'applicationTime', 'adminReviewTime', 'userReviewStatus'}
            #查询到的数据格式为列表
            for item in data:
                nowItem = {}

                nowItem['hours'] = item[2]
                nowItem['statusText'] = statusMapping[item[6]]
                #statusMapping = ['待审核', '审核通过', '审核未通过']
                nowItem['title'] = item[1]
                nowItem['record'] = item[3]
                # nowItem['body'] = '课时主题\n{}\n课时记录\n{}\n'.format(
                #     item[1], item[3])
                nowItem['created_at'] = str(item[4])
                nowItem['updated_at'] = str(item[5])
                nowItem['open'] = False
                ret['data'].append(
                    dict(zip(dataKeys,item))
                )

            ret['code'] = 0
            ret['msg'] = '评论成功'
        except Exception as e:
            ret['msg'] = str(e)

    return makeRespose(ret)
