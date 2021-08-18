import flask
from conf.conf import *
from conf.conn import getCursor
from weChatAPI.utils import *
from utils import *

wx_user = flask.Blueprint("wx_user", __name__)

# 获取用户各阶段课程
@wx_user.route('/api/weChat/user/queryPersonalCourse/<int:status>/<openid>', methods=['GET'])
def queryPersonalCourse(status,openid):
    ret = retModel.copy()
    ret['data']['items'] = []
    uid = getUserIdByopenid(openid)

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
            Cour_UserFee,
            Cour_CreateTime
        FROM tbl_CourseUser LEFT JOIN tbl_Course ON CoUs_CourseId = Cour_Id
        WHERE Cour_DeleteStatus = 0 AND CoUs_UserId=%s AND Cour_Status = %s
        '''
        cs.execute(sql, (int(uid),int(status)))
        data = cs.fetchall()
        dataKeys = ('cid', 'title', 'subject', 'grade', 'remark',
                    'courseTime', 'coursePlace','userFee','createTime')
        for item in data:
            item = list(item)
            item[-1] = str(item[-1])
            ret['data']['items'].append(
                dict(zip(dataKeys, item))
            )
    return makeRespose(ret)


# 获取课程详情#################################################################干嘛用的？？可以优化？？写的太复杂了
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
    
# 获取用户信息##############可以增加
@wx_user.route("/api/weChat/user/getUser/<openid>",methods=['POST'])
def getUser(openid):
    ret = retModel.copy()
    uid = getUserIdByopenid(openid)

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
    
    with getCursor() as cs:
        sql = '''
        INSERT INTO tbl_Course ( Cour_Class, Cour_TeacherId, Cour_Status, Cour_Title, Cour_Subject, Cour_Grade, Cour_Remark, Cour_UserFee, Cour_TeacherFee, Cour_Hours, Cour_ShowStatus, Cour_CourseTime, Cour_CoursePlace )
        VALUES
	        ( '预约课',{}, 1, '待定', '待定', '待定', '无', 0, 0, 0, 0, '待定', '待定' );
        '''.format(tid)
        cs.execute(sql)
        cid = cs.lastrowid
        sql = '''
        INSERT INTO tbl_CourseUser ( CoUs_CourseId, CoUs_UserId, CoUs_Status )
        VALUES
	        (%s, %s, 1);
        '''
        cs.execute(sql,(int(cid),int(uid)))
        sql = '''
        INSERT INTO tbl_CourseTeacher ( CoTe_CourseId, CoTe_TeacherId )
        VALUES
	        (%s, %s)
        '''
        cs.execute(sql,(int(cid),int(tid)))
        sql = '''
        INSERT INTO tbl_Order ( Orde_Type, Orde_CommodityId, Orde_UserId )
        VALUES
	        ('COURSE',%s,%s)
        '''
        cs.execute(sql,(cid,uid))
        ret['msg'] = '预约成功'

    return makeRespose(ret)