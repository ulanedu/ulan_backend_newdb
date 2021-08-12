import flask
from conf.conf import *
from conf.conn import getCursor
from wechatAppAPI_v1.utils import *
from utils import *

wx_student = flask.Blueprint("wx_student", __name__)

# query student's personal course
# tip

@wx_student.route('/api/w_v1/queryPersonalCourse/<openid>')
def queryPersonalCourse(openid):
    ret = wx_retModel.copy()
    ret['data']['items'] = []
    studentId = getStudentIdByopenid(openid)
    with getCursor() as cs:
        sql = '''
        SELECT `courses`.id as courseId,`courses`.title,`courses`.short_description,`courses`.charge,
        `course_personal`.status as courseStatus
        FROM `courses`
        LEFT JOIN `course_personal` ON `course_personal`.courseId = `courses`.id
        WHERE `courses`.category_id = 0 AND `courses`.deleted_at is NULL AND `courses`.user_id=%s
        '''
        cs.execute(sql, studentId)
        data = cs.fetchall()
        dataKeys = ('id', 'title', 'requirement', 'charge', 'courseStatus')
        for item in data:
            item = list(item)
            print(item)
            item[2] = flask.json.loads(item[2])
            ret['data']['items'].append(
                dict(zip(dataKeys, item))
            )
    return makeRespose(ret)


# query student's personal course -detail
@wx_student.route('/api/w_v1/queryPersoanlCourseDetail/<openid>/<courseId>')
def queryPersoanlCourseDetail(openid, courseId):

    ret = {
        'code': 0,
        'data': {
            'attach': [],
            'chapters': [],
            'course': {
                'charge': 0,
                'id': -1,
                'title': 'None',
                'short_description': '暂无课程信息',
            },
            'isBuy': getPersonalCoursePayStatus(int(courseId)),
            'isCollect': False
        },
        'message': ''
    }

    studentId = getStudentIdByopenid(openid)
    with getCursor() as cs:
        sql = '''
        SELECT `courses`.id as courseId,`courses`.title,`courses`.short_description,`courses`.charge,
        `course_personal`.status as courseStatus
        FROM `courses`
        LEFT JOIN `course_personal` ON `course_personal`.courseId = `courses`.id
        WHERE `courses`.category_id = 0 AND `courses`.deleted_at is NULL AND `courses`.user_id=%s AND `courses`.id=%s
        '''
        cs.execute(sql, (int(studentId), int(courseId)))

        data = cs.fetchone()
        if (data):
            ret['data']['course']['id'] = data[0]
            ret['data']['course']['title'] = data[1]
            ret['data']['course']['short_description'] = flask.json.loads(
                data[2])
            ret['data']['course']['charge'] = data[3]
            ret['data']['course']['courseStatus'] = data[4]

    return makeRespose(ret)
    
# 获取学生信息
@wx_student.route("/api/w_v1/getStudentByOpenid/<Openid>",methods=['POST'])
def getStudentByOpenid(Openid):
    ret = wx_retModel.copy()
    Sid = getStudentByOpenid(Openid)
    with getCursor() as cs:
        sql = '''
        SELECT nick_name, mobile
        FROM users
        WHERE id = {}
        '''.format(Sid)
        cs.execute(sql)
        data = cs.fetchone()
        dataKeys=('name','phoneNumber')
        ret['data'] = dict(zip(dataKeys,data))
    return makeRespose(ret)
    
# 预约教师
@wx_student.route('/api/w_v1/reserveTeacher/<openid>/<teacherId>',methods=['POST'])
def reserveTeacher(openid, teacherId):
    print(123)
    studentid = getStudentIdByopenid(openid)
    ret = wx_retModel.copy()
    timestamp = getTimestamp()
    with getCursor() as cs:
        sql = '''
        SELECT * FROM courses,course_personal WHERE courses.id = course_personal.courseId AND courses.user_id = %s AND course_personal.teacherId = %s
        '''         # 需要添加结课条件，结课以后还可以预约
        cs.execute(sql,(studentid,teacherId))
        data = cs.fetchone()
        if data:
            ret['msg'] = "已预约"
            ret['code'] = -1
            return makeRespose(ret)
        
        sql = '''
        INSERT INTO courses(user_id,title,charge,short_description,category_id,published_at,created_at,updated_at,is_show,comment_status,channel)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,1,2,1)
        '''
        # comment_status = 2,仅订阅后可以评论
        requirement = {
            'title': "预约课",
            'subject': "待定",
            'hours': 0,
            'courseTime': "待定",
            'coursePlace': "待定",
            'remarks': "无"
        }
        reqText = flask.json.dumps(requirement)

        try:
            cs.execute(sql,
                       (studentid, "预约课",
                        0, reqText, 0, timestamp, timestamp, timestamp)
                       )
            lastRowId = cs.lastrowid
            
        except Exception as e:
            print(e)
            ret['msg'] = str(e)
            ret['code'] = -1
            return makeRespose(ret)

        sql = '''
        INSERT INTO course_personal(courseId,teacherId,status,orderRecord)
        VALUES (%s,%s,1,%s)
        '''
        orderRecord = {
            'hours': 0,
            'events': []
        }
        try:
            cs.execute(sql, (lastRowId, teacherId, flask.json.dumps(orderRecord)))
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
        
        sql = '''
        INSERT INTO course_teacher_mapping(courseId,teacherId)
        VALUES (%s,%s)
        '''
        try:
            cs.execute(sql, (lastRowId, teacherId))
        except Exception as e:
            print(e)
            ret['msg'] = str(e)
            ret['code'] = -1
    print(ret)
    return makeRespose(ret)
