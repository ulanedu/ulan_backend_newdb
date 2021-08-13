import flask
import redis
from conf.conf import *
from conf.conn import getCursor
from weChatAPI.utils import *
from utils import *

wx_teacher = flask.Blueprint("wx_teacher", __name__)

# 检查是否已注册
@wx_teacher.route('/api/weChat/teacher/isRegistered', methods=['POST'])
def isRegistered():
    params = flask.request.get_json()
    code = params['code']
    openid = getUserOpenId(code)

    isReged = False
    if getTeacherIdByopenid(openid):
        isReged = True

    return makeRespose({'isRegistered': isReged, 'openid': openid})

# 注册（注册->引导完善简历）
@wx_teacher.route('/api/weChat/teacher/register', methods=['POST'])
def register():
    ret = retModel.copy()
    params = flask.request.get_json()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    verifyCode = r.get(params['phoneNumber'])

    if (int(verifyCode) == int(params['captcha'])):
        with getCursor() as cs:
            sql1 = '''
            INSERT INTO tbl_Teacher ( Teac_OpenId, Teac_PhoneNumber )
            VALUES
            	(%s, %s);
            '''
            sql2 = '''
            INSERT INTO tbl_TeacherResume ( TeRe_PhoneNumber )
            VALUES
            	({});
            '''.format(params['phoneNumber'])
            openid = getUserOpenId(params['code'])
            cs.execute(sql1,(openid,params['phoneNumber']))
            cs.execute(sql2)
            ret['msg'] = '注册成功！'
    else:
        ret['msg'] = '验证码错误！'
        ret['code'] = -1

    return makeRespose(ret)


# 教师 查询可接课程(自动过滤已接订单)
@wx_teacher.route('/api/weChat/teacher/getOrders/<openid>', methods=['POST'])
def getOrders(openid):
    ret = retModel.copy()
    ret['data']['items'] = []
    data = flask.request.get_json()
    tid = getTeacherIdByopenid(openid)

    with getCursor() as cs:
        sql = '''
        SELECT
        	Cour_Id,
        	Cour_Title,
        	Cour_Subject,
        	Cour_Grade,
        	Cour_Remark,
        	Cour_CourseTime,
        	Cour_CoursePlace,
        	Cour_TeacherFee,
        	Cour_Hours,
        	Cour_CreateTime 
        FROM
        	tbl_Course 
        WHERE
        	Cour_DeleteStatus = 0 
        	AND Cour_Status = 0 
        	AND Cour_Id NOT IN (
        	SELECT
        		CoTe_CourseId 
        	FROM
        		tbl_CourseTeacher 
        WHERE
        	CoTe_TeacherId = {});
            '''.format(tid)
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('cid', 'title', 'subject', 'grade', 'remark', 'courseTime', 'coursePlace', 'teacherFee', 'hours', 'createTime')
        for item in data:
            item = list(item)
            item[9] = str(item[9])
            ret['data']['items'].append(
                dict(zip(dataKeys,item))
            )

    return makeRespose(ret)

# 投递课程
@wx_teacher.route('/api/weChat/teacher/candidate', methods=['POST'])
def candidate():
    ret = retModel.copy()
    data = flask.request.get_json()
    cid = data['cid']
    tid = getTeacherIdByopenid(data['openid'])

    with getCursor() as cs:
        sql1 = '''
        SELECT
        	Teac_ContractStatus 
        FROM
        	tbl_Teacher 
        WHERE
        	Teac_Id = {}
        '''.format(tid)
        sql2 = '''
        INSERT INTO tbl_CourseTeacher ( CoTe_CourseId, CoTe_TeacherId )
        VALUES
        	(%s, %s)
        '''
        cs.execute(sql1)
        data = cs.fetchone()
        if (int(data[0]) == 0):
            raise Exception("请联系管理员，签约后才能投递哦！")
        cs.execute(sql2, (int(cid),int(tid)))
        ret['msg'] = '投递成功！'

    return makeRespose(ret)

# 取消投递
@wx_teacher.route('/api/weChat/teacher/cancel', methods=['POST'])
def cancel():
    ret = retModel.copy()
    data = flask.request.get_json()
    cid = data['cid']
    tid = getTeacherIdByopenid(data['openid'])

    with getCursor() as cs:
        sql = '''
        DELETE 
        FROM
        	tbl_CourseTeacher 
        WHERE
        	CoTe_CourseId = %s 
        	AND CoTe_TeacherId = %s
        '''
        cs.execute(sql, (int(cid), int(tid)))
        ret['code'] = 0
        ret['msg'] = '已取消投递'

    return makeRespose(ret)

# 获取投递订单
@wx_teacher.route('/api/weChat/teacher/getCandidatedOrders', methods=['POST'])
def GetCandidatedOrders():
    ret = retModel.copy()
    ret['data']['items'] = []
    data = flask.request.get_json()
    openid = data['openid']
    orderStatus = data['orderStatus']
    tid = getTeacherIdByopenid(openid)

    with getCursor() as cs:
        sql = '''
        SELECT
        	Cour_Id,
        	Cour_TeacherId,
        	Cour_Title,
        	Cour_Subject,
        	Cour_Grade,
        	Cour_Remark,
        	Cour_CourseTime,
        	Cour_CoursePlace,
        	Cour_TeacherFee,
        	Cour_Hours,
        	Cour_Status,
        	Cour_CreateTime 
        FROM
        	tbl_CourseTeacher
        	LEFT JOIN tbl_Course ON CoTe_CourseId = Cour_Id 
        WHERE
        	Cour_DeleteStatus = 0 
        	AND Cour_Status = % s 
        	AND CoTe_TeacherId = % s 
        ORDER BY
        	CoTe_Time DESC
        '''
        cs.execute(sql, (int(orderStatus), int(tid)))
        data = cs.fetchall()
        dataKeys = ('cid', 'tid', 'title', 'subject', 'grade', 'remark', 'courseTime', 'coursePlace', 'teacherFee', 'hours', 'status', 'createTime')
        for item in data:
            item = list(item)
            # item[1] : 1(分配给了教员) 0(未分配) -1(分配阶段且未分配给教员)
            if orderStatus > 0:
                if int(item[1]) != tid:
                    continue
                else:
                    item[1] = 1
            else:
                if int(item[1]) != tid:
                    item[1] = -1
                else:
                    item[1] = 0
            item[-1] = str(item[-1])
            ret['data']['items'].append(
                dict(zip(dataKeys,item))
            )
        ret['msg'] = '查询成功'

    return makeRespose(ret)


@wx_teacher.route('/api/wwChat/teacher/dismissalApplication', methods=['POST'])
def dismissalApplication():
    data = flask.request.get_json()
    ret = retModel.copy()

    with getCursor() as cs:
        sql = '''
        INSERT INTO tbl_DismissalApplication ( DiAp_CourseId, DiAp_DismissedHour, DiAp_CourseContent, DiAp_StartTime, DiAp_CourseContent )
        VALUES
	        (% s,% s,% s,% s,% s)
        '''
        cs.execute(sql, (data['cid'],data['dismissedHour'],data['courseContent'],data['startTime'],data['courseContent']))
        ret['msg'] = '申请成功'

    return makeRespose(ret)

# 课程讨论
@wx_teacher.route('/api/weChat/teacher/courseDiscussion', methods=['POST'])
def courseDiscussion():
    data = flask.request.get_json()
    ret = retModel.copy()
    tid = getTeacherIdByopenid(data['openid'])

    with getCursor() as cs:
        sql = '''
        INSERT INTO tbl_CourseDiscussion ( CoDi_CourseId, CoDi_Discussant, CoDi_DiscussantId, CoDi_Content )
        VALUES
        	(%s, 0, %s, %s)
        '''
        cs.execute(sql, (data['cid'],tid,data['content']))
        ret['msg'] = '发布成功'

    return makeRespose(ret)

# 获取教师简历
@wx_teacher.route("/api/weChat/teacher/getTeacherResume",methods=['POST'])
def getTeacherResume():
    ret = retModel.copy()
    data = flask.request.get_json()
    tid = getTeacherIdByopenid(data['openid'])
    
    with getCursor() as cs:
        sql = '''
        SELECT
        	* 
        FROM
        	tbl_TeacherResume 
        WHERE
        	TeRe_Id ={}
        '''.format(tid)
        cs.execute(sql,int(tid))
        data = cs.fetchone()
        dataKeys=('tid','name','sex','nation','politics','email','skilled','hobbies','school','major','grade','honour','teachExp','evaluation','free_time','avatarURL','phone_number')
        ret['data']=dict(zip(dataKeys, data))
    return makeRespose(ret)

# 修改简历
@wx_teacher.route('/api/weChat/teacher/updateResume', methods=['POST'])
def updateResume():
    data = flask.request.get_json()
    ret = retModel.copy()
    openid = data['openid']
    data = data['form']
    tid = getTeacherIdByopenid(openid)
    with getCursor() as cs:
        sql_v2 = '''
        UPDATE tbl_TeacherResume 
        SET TeRe_Name = %s,
        TeRe_Sex = %s,
        TeRe_Nation = %s,
        TeRe_PoliticalStatus = %s,
        TeRe_Email = %s,
        TeRe_GoodSubjects = %s,
        TeRe_Hobby = %s,
        school = %s,
        TeRe_Major = %s,
        TeRe_Grade = %s,
        TeRe_Honors = %s,
        TeRe_TeachExperience = %s,
        TeRe_SelfEvaluation = %s,
        TeRe_AvatarURL = %s,
        TeRe_FreeTime = %s,
        TeRe_PhoneNumber = %s 
        WHERE
        	TeRe_Id = %s
        '''
        cs.execute(sql_v2,(data['name'],data['sex'],data['nation'],data['politics'],data['email'],data['skilled'],data['hobbies'],data['school'],data['major'],data['grade'],data['honour'],data['teachExp'],data['evaluation'],data['avatarURL'],data['free_time'],data['phone_number'],int(tid)))
        ret['msg'] = '修改成功'

    return makeRespose(ret)
