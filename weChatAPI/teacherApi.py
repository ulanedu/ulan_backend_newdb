import flask
import redis
import time
from conf.conf import *
from conf.conn import getCursor
from weChatAPI.utils import *
from utils import *

wx_teacher = flask.Blueprint("wx_teacher", __name__)


@wx_teacher.route('/api/weChat/teacher/isRegistered', methods=['POST'])
def getTeacherId():
    data = flask.request.get_json()
    code = data['code']
    openid = getUserOpenId(code)

    isReged = False

    with getCursor() as cs:
        sql = 'SELECT Teac_id  FROM `tbl_Teacher` WHERE wechat_openid=%s'

        cs.execute(sql, openid)
        data = cs.fetchone()
        if (data):
            isReged = True

    return makeRespose({'isRegistered': isReged, 'openid': openid})


@wx_teacher.route('/api/weChat/teacher/register', methods=['POST'])
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
            tbl_Teacher(Teac_ContractStatus,Teac_OpenId,Teac_PhoneNumber)
            VALUES (0,%s)
            '''#Teac_ContractStatus 签约状态(0未签约，1已签约)
            sql2 = '''
            INSERT INTO
            tbl_TeacherResume (TeRe_Id,TeRe_Name,TeRe_School,TeRe_Major,TeRe_FreeTime)
            SELECT uid,%s,%s,%s,%s
            FROM tbl_Teacher
            WHERE Teac_OpenId = %s
            '''#新数据库表 teacher 手机号由tbl_TeacherResume改存在 tbl_Teacher
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
@wx_teacher.route('/api/weChat/teacher/getOrders', methods=['POST'])
def teacherGetOrders():
    ret = {
        'orderList': []
    }

    data = flask.request.get_json()
    openid = data['openid']
    tid = getTeacherIdByopenid(openid)

    with getCursor() as cs:
        sql = '''
        SELECT
        `tbl_Course`.Cour_Id,`tbl_Course`.Cour_Title,
        `tbl_Courses`.Cour_Subject,`tbl_Courses`.Cour_Grade,`tbl_Courses`.Cour_Remark,
        `tbl_Courses`.Cour_CourseTime, `tbl_Courses`.Cour_CoursePlace,`tbl_Courses`.Cour_UserFee,Cour_Hours
        `tbl_Course`.Cour_CreateTime
        FROM
        tbl_Course
        LEFT JOIN `tbl_CourseUser` ON `tbl_CourseUser`.CoUs_CourseId = `tbl_Courses`.Cour_Id
        WHERE  `tbl_Courses`.Cour_DeleteStatus = 0 
        AND `tbl_Courses`.Cour_Status = 0
        AND `tbl_Courses`.Cour_CompletedHours = 0 
        ORDER BY `tbl_Courses`.Cour_CreateTime DESC
        '''#tbl_Courses   课程状态(0分配教员，1试课中，2开课，3已结课)
        cs.execute(sql)

        data = cs.fetchall()

        for item in data:
            retItem = {}
            retItem['id'] = item[0]
            retItem['title'] = item[1]
#这里用了奇怪的写法
            if type(item[-1]) == type('a'):
                retItem['publicTime'] = item[-1]
            else:
                retItem['publicTime'] = item[-1].strftime("%Y-%m-%d %H:%M")

            # detail = flask.json.loads(item[2])
            # retItem['classTime'] = detail['courseTime']
            # retItem['classPlace'] = detail['coursePlace']
            # retItem['orderRequire'] = detail['remarks']
            # retItem['subject'] = detail['subject']
            # retItem['classHours'] = detail['hours']
            #
            # ret['orderList'].append(retItem)
            # detail = flask.json.loads(item[2])
            retItem['subject'] = item[2]
            retItem['grade'] = item[3]
            retItem['remark'] = item[4]
            retItem['coursetime'] = item[5]
            retItem['courseplace'] = item[6]
            retItem['charge'] = item[7]
            retItem['hours'] = item[8]

            ret['orderList'].append(retItem)


    return makeRespose(ret)


@wx_teacher.route('/api/weChat/teacher/teacherCandidate', methods=['POST'])
def teacherCandidate():
    data = flask.request.get_json()
    orderId = data['orderId']
    openid = data['openid']
    tid = getTeacherIdByopenid(openid)

    ret = {
        'code': -1,
        'msg': ''
    }

    if(teacherStatus == 1):
        with getCursor() as cs:
            sql1 = '''
            SELECT 1 FROM  tbl_Courses
            WHERE Cour_Id = %s AND Cour_Status = 0
            '''
            sql2 = '''
            SELECT 1 FROM `tbl_CourseTeacher`
            WHERE CoTe_CourseId = %s AND CoTe_TeacherId = %s
            '''
            sql3 = '''
            INSERT INTO `tbl_CourseTeacher` (CoTe_CourseId, CoTe_TeacherId ) VALUES (%s,%s)
            '''
            try:
                cs.execute(sql1, int(orderId))
                isExist = cs.fetchone()
                if (isExist):
                    cs.execute(sql2, (int(orderId), tid))
                    isCandidated = cs.fetchone()
                    if (isCandidated):
                        ret['msg'] = '请勿重复投递'
                    else:
                        cs.execute(sql3, (int(orderId), tid))
                        ret['code'] = 1
                        ret['msg'] = '投递成功,可至“我的订单”查看投递进度'
                else:
                    ret['msg'] = '无订单信息，请刷新后再试'
            except Exception as e:
                ret['msg'] = str(e)

    # 逻辑改变！！！！！
    elif (teacherStatus == -1):
        ret['msg'] = '只有审核通过后才能接单喔'
    else:
        ret['msg'] = '查无教师信息，请联系管理员处理'

    return makeRespose(ret)


@wx_teacher.route('/api/weChat/teacher/cancel', methods=['POST'])
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
        sql1_v2 = '''
        DELETE FROM `tbl_CourseTeacher` WHERE CoTe_CourseId = %s AND  CoTe_TeacherId  = %s
        '''
        try:
            cs.execute(sql1_v2, (int(courseId), int(teacherId)))
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
            sql_v2 = '''
            SELECT
            `tbl_Course`.Cour_Id,
            `tbl_Course`.Cour_Title,
            
            `tbl_Courses`.Cour_Subject,`tbl_Courses`.Cour_Grade,`tbl_Courses`.Cour_Remark,
            `tbl_Courses`.Cour_CourseTime, `tbl_Courses`.Cour_CoursePlace,`tbl_Courses`.Cour_UserFee,Cour_Hours
            
            `tbl_Course`.Cour_Status,
            `tbl_CourseTeacher`.created_at
            FROM
            `tbl_CourseTeacher`
            LEFT JOIN `tbl_Course` ON `tbl_CourseTeacher`.CoTe_CourseId = `tbl_Courses`.Cour_Id
            LEFT JOIN `tbl_CourseUser` ON `tbl_CourseTeacher`.CoTe_CourseId = `tbl_CourseUser`.CoUs_CourseId
            WHERE  `tbl_Courses`.Cour_DeleteStatus = 0 
            AND `tbl_Course`.Cour_Status = %s
            AND `tbl_CourseTeacher`.CoTe_TeacherId = %s
            ORDER BY `tbl_CourseTeacher`.CoTe_Time DESC
            '''#`course_personal`.status = %s?????????????    channle
            cs.execute(sql_v2, (int(orderStatus), int(teacherId)))
            data = cs.fetchall()
            print(data)

            for item in data:
                retItem = {}
                retItem['id'] = item[0]
                retItem['title'] = item[1]

                retItem['channel'] = 0
                retItem['publicTime'] = item[-1].strftime("%Y-%m-%d %H:%M")
                retItem['orderStatus'] = item[-2]
                retItem['createdTime'] = item[-1].strftime("%Y-%m-%d %H:%M")

                # detail = flask.json.loads(item[2])
                # retItem['classTime'] = detail['courseTime']
                # retItem['classPlace'] = detail['coursePlace']
                # retItem['orderRequire'] = detail['remarks']
                # retItem['subject'] = detail['subject']
                # retItem['classHours'] = detail['hours']
                retItem['subject'] = item[2]
                retItem['grade'] = item[3]
                retItem['orderRequire'] = item[4]
                retItem['classTime'] = item[5]
                retItem['classPlace'] = item[6]
                retItem['charge'] = item[7]
                retItem['classHours'] = item[8]

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
        sql1_v2 = '''
                INSERT INTO `tbl_DismissalApplication` (DiAp_CourseId,DiAp_DismissedHour,DiAp_CourseContent,DiAp_ApplicationTime) VALUES
                (%s,%s,%s,%s,%s,%s)
                '''#不需要teacherid了
        try:
            params = (int(courseId), int(
                hours),  record, timestamp)
            cs.execute(sql1_v2, params)
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
        sql1_v2 = '''
                INSERT INTO `tbl_CourseDiscussion` (CoDi_DiscussantId,CoDi_CourseId,CoDi_Content,CoDi_Time) VALUES
                (%s,%s,%s,%s)
                '''
        try:
            params = (-int(teacherId), int(courseId),
                      "<p>{}</p>".format(original_content), timestamp)
            cs.execute(sql1_v2, params)
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
        sql_v2 = '''
        SELECT *
        FROM tbl_TeacherResume
        WHERE TeRe_Id=%s
        '''
        cs.execute(sql_v2,int(Tid))
        data = cs.fetchone()
        print(Tid)
        dataKeys=('Tid','name','sex','nation','politics','email','skilled','hobbies','school','major','grade','honour','teachExp','evaluation','free_time','avatarURL','phone_number')
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
        sql_v2 = '''
                UPDATE tbl_TeacherResume
                SET TeRe_Name=%s,TeRe_Sex=%s,TeRe_Nation=%s,TeRe_PoliticalStatus=%s,TeRe_Email=%s,TeRe_GoodSubjects=%s,TeRe_Hobby=%s,school=%s
                ,TeRe_Major=%s,TeRe_Grade=%s,TeRe_Honors=%s,TeRe_TeachExperience=%s,TeRe_SelfEvaluation=%s,TeRe_AvatarURL=%s,TeRe_FreeTime=%s,TeRe_PhoneNumber=%s
                WHERE TeRe_Id = %s
                '''
        sql2_v2 = '''
                        UPDATE tbl_Teacher
                        SET Teac_PhoneNumber=%s
                        WHERE Teac_Id = %s
                        '''#phone
        try:
            cs.execute(sql_v2,(data['name'],data['sex'],data['nation'],data['politics'],data['email'],data['skilled'],data['hobbies'],data['school'],data['major'],data['grade'],data['honour'],data['teachExp'],data['evaluation'],data['avatarURL'],data['free_time'],data['phone_number'],int(Tid)))
            cs.execute(sql2_v2, (
             data['phone_number']))

            ret['code'] = 0
            ret['msg'] = '修改成功'
            print(data['name'])
        except Exception as e:
            ret['msg'] = str(e)
            print(e)

    return makeRespose(ret)
