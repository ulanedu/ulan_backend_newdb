import flask
from conf.conf import *
from conf.conn import getCursor
from weChatAPI.utils import *
from utils import *

wx_user = flask.Blueprint("wx_user", __name__)


@wx_user.route('/api/weChat/user/queryPersonalCourse/<openid>')
def queryPersonalCourse(openid):
    ret = retModel.copy()
    ret['data']['items'] = []
    userId = getUserIdByopenid(openid)
    with getCursor() as cs:
        sql = '''
        SELECT `tbl_Courses`.Cour_Id as courseId,`tbl_Courses`.Cour_Title,`tbl_Courses`.Cour_Subject,`tbl_Courses`.Cour_Grade,`tbl_Courses`.Cour_Remark,
        `tbl_Courses`.Cour_CourseTime, `tbl_Courses`.Cour_CoursePlace,`tbl_Courses`.Cour_UserFee,
        `tbl_Courses`.Cour_Status as courseStatus
        FROM `tbl_Courses`
        LEFT JOIN `tbl_CourseUser` ON `tbl_CourseUser`.CoUs_CourseId = `tbl_Courses`.Cour_Id
        WHERE  `tbl_Courses`.Cour_DeleteStatus = 0 AND `tbl_CourseUser`.CoUs_UserId={}
        '''.format(userId)
        #short_description
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('cid', 'title', 'subject', 'grade', 'remark',
                    'courseTime', 'coursePlace','charge', 'courseStatus', )
        for item in data:
            item = list(item)
            item[5] = str(item[5])
            ret['data']['items'].append(
                dict(zip(dataKeys, item))
            )
    return makeRespose(ret)


# query student's personal course -detail
@wx_user.route('/api/weChat/user/queryPersoanlCourseDetail/<openid>/<courseId>')
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
                'subject':'None',
                'garde':'None',
                'remark':'暂无',
                'coursetime':'待定',
                'courseplace':'待定'
                #'short_description': '暂无课程信息',
            },
            'isBuy': getPersonalCoursePayStatus(int(courseId)),
            'isCollect': False
        },
        'message': ''
    }

    userId = getUserIdByopenid(openid)
    with getCursor() as cs:
        sql = '''
        SELECT `tbl_Courses`.Cour_Id as courseId,`tbl_Courses`.Cour_Title,
        `tbl_Courses`.Cour_Subject,`tbl_Courses`.Cour_Grade,`tbl_Courses`.Cour_Remark,
        `tbl_Courses`.Cour_CourseTime, `tbl_Courses`.Cour_CoursePlace,
        `tbl_Courses`.Cour_UserFee,
        `tbl_Courses`.Cour_Status as courseStatus
        FROM `tbl_Courses`
        LEFT JOIN `tbl_CourseUser` ON `tbl_CourseUser`.CoUs_CourseId = `tbl_Courses`.Cour_Id
        WHERE `courses`.category_id = 0 AND `tbl_Course`.Cour_DeleteStatus = 0 AND `tbl_CourseUser`.CoUs_UserId=%s AND `tbl_Courses`.Cour_Id=%s
        '''
        # **************************************************************************************************************************************************
        # short_description
        cs.execute(sql, (int(userId), int(courseId)))

        data = cs.fetchone()
        if (data):
            ret['data']['course']['id'] = data[0]
            ret['data']['course']['title'] = data[1]
            # ret['data']['course']['short_description'] = flask.json.loads(
            #     data[2])
            #**********************************************
            ret['data']['course']['subject'] = data[2]
            ret['data']['course']['grade'] = data[3]
            ret['data']['course']['remark'] = data[4]
            ret['data']['course']['coursetime'] = data[5]
            ret['data']['course']['courseplace'] = data[6]
            #**********************************************
            ret['data']['course']['charge'] = data[-2]
            ret['data']['course']['courseStatus'] = data[-1]#前面貌似字典里没这个键

    return makeRespose(ret)
    
# 获取用户信息
@wx_user.route("/api/weChat/user/getUserByOpenid/<Openid>",methods=['POST'])
def getUserByOpenid(Openid):
    ret = retModel.copy()
    uid = getUserIdByopenid(Openid)
    with getCursor() as cs:
        sql = '''
        SELECT UsIn_StudentName, UsIn_PhoneNumber
        FROM tbl_UserInfo
        WHERE UsIn_Id = {}
        '''.format(uid)

        cs.execute(sql)
        data = cs.fetchone()
        dataKeys=('name','phoneNumber')

        ret['data'] = dict(zip(dataKeys,data))

    return makeRespose(ret)
    
# 预约教师
@wx_user.route('/api/weChat/user/reserveTeacher/<openid>/<tid>',methods=['POST'])
def reserveTeacher(openid, tid):
    uid = getUserIdByopenid(openid)
    ret = retModel.copy()
    timestamp = getTimestamp()
    with getCursor() as cs:
        sql = '''
        INSERT INTO courses(user_id,title,charge,short_description,category_id,published_at,created_at,updated_at,is_show,comment_status,channel)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,1,2,1)
        '''

        #新数据库拆分为两部分，需要进行两次插入
        sql_v2 = '''
                INSERT INTO tbl_Course(Cour_Title,Cour_UserFee,Cour_Subject,Cour_Grade,Cour_Remark,Cour_CourseTime, Cour_CoursePlace,Cour_CreateTime
                ,Cour_ShowStatus,Cour_DeleteStatus,Cour_Status)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,1,0,0)
                '''#Cour_Id设置为自动递增，插入tbl_CourseUser前需要获取Cour_Id的当前即最大值
        # comment_status = 2,仅订阅后可以评论  Cour_Status = 0 表示 分配教员  Cour_DeleteStatus = 0  表示 未删除
        sql_Cour_Id = ''' select max(Cour_Id) from tbl_Course'''
        num = cs.execute(sql_Cour_Id)
        CoUs_CourseId = cs.fetchall()[0][0]
        print("CoUs_CourseId:", CoUs_CourseId)#貌似就是lastRowId，多余的一步

        sql1_v2 = '''
        insert into tbl_CourseUser(CoUs_CourseId,CoUs_UserId)
        values(%s,%s)
        '''#,CoUs_Time,CoUs_Status  时间和课程状态 设置了默认值

        #**********************************************************************************************
        # requirement = {
        #     'title': "预约课",
        #     'subject': "待定",
        #     'hours': 0,
        #     'courseTime': "待定",
        #     'coursePlace': "待定",
        #     'remarks': "无"
        # }
        # reqText = flask.json.dumps(requirement)
        #Cour_Subject待定 Cour_Grade待定  Cour_Remark 无 Cour_Hours  Cour_CompletedHours 两个默认设置为零，可以不赋值插入 Cour_CourseTime 待定 Cour_CoursePlace 待定
        try:
            cs.execute(sql_v2,
                       ( "预约课",
                        0, '待定','待定','无','待定','待定',timestamp)
                       )#部分修改 2021.8.7 LD,删去category_id  studentid
            cs.execute(sql1_v2,
                       (CoUs_CourseId,uid)
                       )
            lastRowId = cs.lastrowid
            
        except Exception as e:
            print(e)
            ret['msg'] = str(e)
            ret['code'] = -1
            return makeRespose(ret)

        sql = '''
        INSERT INTO course_teacher_mapping(courseId,teacherId)
        VALUES (%s,%s)
        '''
        sql_v2 = '''
                INSERT INTO tbl_CourseTeacher(CoTe_CourseId,CoTe_TeacherId)
                VALUES (%s,%s)
                '''
        try:
            cs.execute(sql_v2, (lastRowId, tid))
        except Exception as e:
            print(e)
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)