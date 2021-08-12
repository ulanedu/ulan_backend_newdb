import flask
import redis
import time
from conf.conf import *
from conf.conn import getCursor
from weChatAPI.utils import *
from utils import *

wx_teacher = flask.Blueprint("wx_teacher", __name__)


@wx_teacher.route('/api/w_v1/teacher/isRegistered', methods=['POST'])
def getTeacherId():
    data = flask.request.get_json()
    code = data['code']
    openid = getUserOpenId(code)

    isReged = False

    with getCursor() as cs:
        sql = 'SELECT uid FROM `teacher` WHERE wechat_openid=%s'
        cs.execute(sql, openid)
        data = cs.fetchone()
        if (data):
            isReged = True

    return makeRespose({'isRegistered': isReged, 'openid': openid})


@wx_teacher.route('/api/w_v1/teacher/register', methods=['POST'])
def teacherRegister():
    data = flask.request.get_json()['form']
    print(data)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    verifyCode = r.get(data['phone_number'])

    ret = {
        'code': 1002
    }

    if(int(verifyCode) == int(data['captcha'])):
        with getCursor() as cs:
            sql1 = '''
            INSERT INTO
            teacher(teacher_status,wechat_openid)
            VALUES (0,%s)
            '''
            sql2 = '''
            INSERT INTO
            teacher_resume (uid,name,phone_num,school,major,free_time)
            SELECT uid,%s,%s,%s,%s,%s
            FROM teacher
            WHERE wechat_openid = %s
            '''
            openid = getUserOpenId(data['code'])
            requirement = {
            'name': data['name'],
            # 'sex': data['sex'],
            # 'nation': data['nation'],
            # 'native_place': data['nativePlace'],
            # 'politics': data['politics'],
            # 'email': data['email'],
            'phone_num': data['phone_number'],
            # 'skilled': data['skilled'],
            # 'hobbies': data['hobbies'],
            'school': data['school'],
            # 'college': data['college'],
            'major': data['major'],
            # 'grade': data['grade'],
            # 'honour': data['honour'],
            # 'teach_exp': data['teachExp'],
            # 'evaluation': data['evaluation'],
            # 'avatar_url': data['avatarURL'],
            'free_time': data['free_time']
            }
            try:
                cs.execute(sql1,openid)
                cs.execute(sql2,(data['name'],data['phone_number'],data['school'],data['major'],data['free_time'],openid))
                ret['code'] = 1000
            except Exception as e:
                ret['msg'] = str(e)
    else:
        ret['code'] = 1001

    return makeRespose(ret)


# 教师 查询可接订单
@wx_teacher.route('/api/w_v1/teacher/getOrders', methods=['POST'])
def teacherGetOrders():
    ret = {
        'orderList': []
    }

    data = flask.request.get_json()
    openid = data['openid']
    teacherId, _ = getTeacherBaseInfoByopenid(openid)

    with getCursor() as cs:
        sql = '''
        SELECT
        `courses`.id,`courses`.title,`courses`.short_description,`courses`.updated_at
        FROM
        courses
        LEFT JOIN `course_personal` ON `courses`.id = `course_personal`.courseId
        WHERE `courses`.category_id=0 
        AND `courses`.deleted_at IS NULL 
        AND `course_personal`.status = 0
        AND `courses`.id NOT IN (SELECT courseId FROM `course_teacher_mapping` WHERE teacherId =%s)
        ORDER BY `courses`.updated_at DESC
        '''
        cs.execute(sql, teacherId)

        data = cs.fetchall()

        for item in data:
            retItem = {}
            retItem['id'] = item[0]
            retItem['title'] = item[1]
#这里用了奇怪的写法
            if type(item[3]) == type('a'):
                retItem['publicTime'] = item[3]
            else:
                retItem['publicTime'] = item[3].strftime("%Y-%m-%d %H:%M")

            detail = flask.json.loads(item[2])
            retItem['classTime'] = detail['courseTime']
            retItem['classPlace'] = detail['coursePlace']
            retItem['orderRequire'] = detail['remarks']
            retItem['subject'] = detail['subject']
            retItem['classHours'] = detail['hours']

            ret['orderList'].append(retItem)

    return makeRespose(ret)


@wx_teacher.route('/api/w_v1/teacher/candidate', methods=['POST'])
def teacherCandidate():
    data = flask.request.get_json()
    orderId = data['orderId']
    openid = data['openid']
    teacherId, teacherStatus = getTeacherBaseInfoByopenid(openid)

    ret = {
        'code': -1,
        'msg': ''
    }

    if(teacherStatus == 1):
        with getCursor() as cs:
            sql1 = '''
            SELECT 1 FROM `course_personal`
            WHERE `courseId` = %s AND `status` = 0
            '''
            sql2 = '''
            SELECT 1 FROM `course_teacher_mapping`
            WHERE courseId = %s AND teacherId = %s
            '''
            sql3 = '''
            INSERT INTO `course_teacher_mapping` (courseId,teacherId) VALUES (%s,%s)
            '''
            try:
                cs.execute(sql1, int(orderId))
                isExist = cs.fetchone()
                if (isExist):
                    cs.execute(sql2, (int(orderId), teacherId))
                    isCandidated = cs.fetchone()
                    if (isCandidated):
                        ret['msg'] = '请勿重复投递'
                    else:
                        cs.execute(sql3, (int(orderId), teacherId))
                        ret['code'] = 1
                        ret['msg'] = '投递成功,可至“我的订单”查看投递进度'

                else:
                    ret['msg'] = '无订单信息，请刷新后再试'
            except Exception as e:
                ret['msg'] = str(e)
    elif (teacherStatus == -1):
        ret['msg'] = '只有审核通过后才能接单喔'
    else:
        ret['msg'] = '查无教师信息，请联系管理员处理'

    return makeRespose(ret)


@wx_teacher.route('/api/w_v1/teacher/cancel', methods=['POST'])
def teacherCancel():
    data = flask.request.get_json()
    courseId = data['courseId']
    openid = data['openid']
    teacherId, teacherStatus = getTeacherBaseInfoByopenid(openid)

    ret = {
        'code': -1,
        'msg': ''
    }

    with getCursor() as cs:
        sql1 = '''
        DELETE FROM `course_teacher_mapping` WHERE courseId = %s AND teacherId = %s
        '''
        try:
            cs.execute(sql1, (int(courseId), int(teacherId)))
            ret['code'] = 0
            ret['msg'] = '已取消投递'
        except Exception as e:
            ret['msg'] = str(e)

    return makeRespose(ret)


@wx_teacher.route('/api/w_v1/teacher/getMyOrders', methods=['POST'])
def teacherGetCandidatedOrders():

    data = flask.request.get_json()
    openid = data['openid']
    orderStatus = data['orderStatus']
    teacherId, teacherStatus = getTeacherBaseInfoByopenid(openid)
    print(teacherId)
    ret = {
        'code': -1,
        'orderList': [],
        'msg': '暂无订单'
    }

    if(teacherStatus == 1):
        with getCursor() as cs:
            sql = '''
            SELECT
            `courses`.id,`courses`.title,`courses`.short_description,`courses`.updated_at,`courses`.channel,
            `course_personal`.status,
            `course_teacher_mapping`.created_at
            FROM
            `course_teacher_mapping`
            LEFT JOIN `courses` ON `course_teacher_mapping`.courseId = `courses`.id
            LEFT JOIN `course_personal` ON `course_teacher_mapping`.courseId = `course_personal`.courseId
            WHERE `courses`.category_id=0 
            AND `courses`.deleted_at IS NULL 
            AND `course_personal`.status = %s
            AND `course_teacher_mapping`.teacherId = %s
            ORDER BY `course_teacher_mapping`.id DESC
            '''
            cs.execute(sql, (int(orderStatus), int(teacherId)))
            data = cs.fetchall()
            print(data)

            for item in data:
                retItem = {}
                retItem['id'] = item[0]
                retItem['title'] = item[1]
                retItem['channel'] = item[4]
                retItem['publicTime'] = item[3].strftime("%Y-%m-%d %H:%M")
                retItem['orderStatus'] = item[5]
                retItem['createdTime'] = item[6].strftime("%Y-%m-%d %H:%M")

                detail = flask.json.loads(item[2])
                retItem['classTime'] = detail['courseTime']
                retItem['classPlace'] = detail['coursePlace']
                retItem['orderRequire'] = detail['remarks']
                retItem['subject'] = detail['subject']
                retItem['classHours'] = detail['hours']

                ret['orderList'].append(retItem)

            ret['msg'] = '查询成功'
            ret['code'] = 0

    return makeRespose(ret)


@wx_teacher.route('/api/w_v1/teacher/addRecord', methods=['POST'])
def teacherAddRecord():
    data = flask.request.get_json()
    courseId = data['courseId']
    openid = data['openid']
    hours = data['hours_num']
    title = data['hours_title']
    record = data['hours_record']
    timestamp = getTimestamp()
    teacherId, teacherStatus = getTeacherBaseInfoByopenid(openid)

    ret = {
        'code': -1,
        'msg': ''
    }

    with getCursor() as cs:
        sql1 = '''
        INSERT INTO `course_personal_records` (courseId,teacherId,hours,title,record,created_at) VALUES
        (%s,%s,%s,%s,%s,%s)
        '''
        try:
            params = (int(courseId), teacherId, int(
                hours), title, record, timestamp)
            cs.execute(sql1, params)
            ret['code'] = 0
            ret['msg'] = '记录成功'
        except Exception as e:
            ret['msg'] = str(e)

    return makeRespose(ret)


@wx_teacher.route('/api/w_v1/teacher/comment', methods=['POST'])
def teacherComment():
    data = flask.request.get_json()
    courseId = data['courseId']
    openid = data['openid']
    original_content = data['content']

    timestamp = getTimestamp()
    teacherId, teacherStatus = getTeacherBaseInfoByopenid(openid)

    ret = {
        'code': -1,
        'msg': ''
    }

    with getCursor() as cs:
        sql1 = '''
        INSERT INTO `course_comments` (user_id,course_id,original_content,render_content,created_at,updated_at) VALUES
        (%s,%s,%s,%s,%s,%s)
        '''
        try:
            params = (-int(teacherId), int(courseId), original_content,
                      "<p>{}</p>".format(original_content), timestamp, timestamp)
            cs.execute(sql1, params)
            ret['code'] = 0
            ret['msg'] = '评论成功'
        except Exception as e:
            ret['msg'] = str(e)

    return makeRespose(ret)

# 获取教师简历
@wx_teacher.route("/api/w_v1/teacher/getTeacherResume",methods=['POST'])
def getTeacherResume():
    ret = retModel.copy()
    
    data = flask.request.get_json()
    openid = data['openid']
    Tid, _ = getTeacherBaseInfoByopenid(openid)
    
    with getCursor() as cs:
        sql = '''
        SELECT *
        FROM teacher_resume
        WHERE uid=%s
        '''
        cs.execute(sql,int(Tid))
        data = cs.fetchone()
        print(Tid)
        dataKeys=('Tid','name','sex','nation','politics','email','phone_number','skilled','hobbies','school','major','grade','honour','teachExp','evaluation','avatarURL','free_time')
        ret['data']=dict(zip(dataKeys, data))
    return makeRespose(ret)

# 修改简历
@wx_teacher.route('/api/w_v1/teacher/updateResume', methods=['POST'])
def updateResume():
    data = flask.request.get_json()
    openid = data['openid']
    data = data['form']
    print(data)

    ret = {
        'code': -1,
        'msg': ''
    }
    
    Tid, _ = getTeacherBaseInfoByopenid(openid)
    print(Tid)
    with getCursor() as cs:
        sql = '''
        UPDATE teacher_resume
        SET name=%s,sex=%s,nation=%s,politics=%s,email=%s,phone_num=%s,skilled=%s,hobbies=%s,school=%s,major=%s,grade=%s,honour=%s,teach_exp=%s,evaluation=%s,avatar_url=%s,free_time=%s
        WHERE uid = %s
        '''
        try:
            cs.execute(sql,(data['name'],data['sex'],data['nation'],data['politics'],data['email'],data['phone_number'],data['skilled'],data['hobbies'],data['school'],data['major'],data['grade'],data['honour'],data['teachExp'],data['evaluation'],data['avatarURL'],data['free_time'],int(Tid)))
            ret['code'] = 0
            ret['msg'] = '修改成功'
            print(data['name'])
        except Exception as e:
            ret['msg'] = str(e)
            print(e)

    return makeRespose(ret)
    
# 筛选教师
@wx_teacher.route('/api/w_v1/teacher/filterTeachers', methods=['POST'])
def filterTeachers():
    ret = retModel.copy()
    data = flask.request.get_json()
    print(data)
    data = data['subjects']
    skilled = "\'%"
    for i in range(len(data)):
        skilled = skilled + data[i] + "%"
    skilled = skilled + "\'"
    ret = retModel.copy()
    ret['data']['items']=[]
    with getCursor() as cs:
        sql = '''
        SELECT teacher_resume.uid,teacher_resume.name,teacher_resume.school,teacher_resume.major,teacher_resume.phone_num,teacher_resume.skilled,teacher_resume.honour,teacher_resume.evaluation,teacher_resume.avatar_url
        FROM teacher, teacher_resume
        WHERE teacher.uid=teacher_resume.uid and teacher.teacher_status = 1 and teacher_resume.skilled like 
        ''' + skilled
        print(sql)
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys=('Tid','name','school','major','phoneNumber','skilled','honour','evaluation','avatar_url')
        for items in data:
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
    return makeRespose(ret)
        