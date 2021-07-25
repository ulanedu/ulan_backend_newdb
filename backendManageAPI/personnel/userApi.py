import flask
from werkzeug import datastructures
from conf.conn import getCursor
from conf.conf import *

user = flask.Blueprint("user", __name__)

@user.route('/api/backendManage/personnel/user/getUsers/<int:status>', methods=['GET'])
def getUsers(status):
    ret = retModel.copy()
    studentName = '%'+(flask.request.args.get('studentName')or'')+'%'
    phoneNumber = '%'+(flask.request.args.get('phoneNumber')or'')+'%'
    ret['data']['items'] = []
    page = int(flask.request.args.get('page'))
    perPage = int(flask.request.args.get('perPage'))
    orderDir = flask.request.args.get('orderDir') or 'ASC'
    with getCursor() as cs:
        sql = '''
        SELECT
	        User_Id,
	        UsIn_StudentName,
	        UsIn_StudentSchool,
	        UsIn_StudentGrade,
	        UsIn_ParentName,
	        UsIn_PhoneNumber 
        FROM
	        tbl_User,
	        tbl_UserInfo 
        WHERE
	        User_Id = UsIn_Id 
	        AND User_DefriendStatus = % s 
	        AND UsIn_StudentName LIKE % s 
	        AND UsIn_PhoneNumber LIKE % s 
        ORDER BY
	        User_Id
        '''+orderDir
        cs.execute(sql,(status,studentName,phoneNumber))
        data = cs.fetchall()
        dataKeys = ('uid', 'studentName', 'school', 'grade', 'parentName', 'phoneNumber')
        begin = (page-1)*perPage
        end = begin + min(perPage,len(data)-begin)
        for items in data[begin:end]:
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
        ret['data']['count'] = len(data)
    print(ret)
    return makeRespose(ret)

# 查看用户信息
@user.route('/api/backendManage/personnel/user/getUserInfo/<int:uid>', methods=['GET'])
def getUserInfo(uid):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        SELECT
	        * 
        FROM
	        tbl_UserInfo 
        WHERE
	        UsIn_Id = {}
        '''.format(uid)
        cs.execute(sql)
        data = cs.fetchone()
        dataKeys = ('uid', 'studentName', 'studentSex', 'studentSchool', 'studentGrade', 'parentName', 'parentRelation', 'coursePlace', 'avatarURL', 'phoneNumber')
        ret['data'] = dict(zip(dataKeys,data))
    return makeRespose(ret)

# 查看用户订单记录
@user.route('/api/backendManage/personnel/user/getUserOrders/<int:id>', methods=['GET'])
def getUserOrders(id):
    ret = retModel.copy()
    ret['data']['items'] = []
    page = int(flask.request.args.get('page'))
    perPage = int(flask.request.args.get('perPage'))
    orderDir = flask.request.args.get('orderDir') or 'DESC'
    with getCursor() as cs:
        sql = '''
        SELECT
	        * 
        FROM
	        tbl_Order 
        WHERE
	        Orde_UserId = {} 
        ORDER BY
	        Orde_Id
        '''.format(id)+orderDir
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('oid', 'type', 'commodityId', 'userId', 'amount', 'paymentStatus', 'paymentGateway', 'paymentMethod', 'paymentTime')
        begin = (page-1)*perPage
        end = begin + min(perPage,len(data)-begin)
        for items in data[begin:end]:
            items = list(items)
            items[8] = str(items[8])
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
        ret['data']['count'] = len(data)
    return makeRespose(ret)

# 获取订单信息
@user.route('/api/backendManage/personnel/user/getOrderDetail/<int:cid>',methods=['GET'])
def getCourse(cid):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        SELECT
            Cour_Class,
            Cour_CreateTime,
            Cour_Hours,
            Cour_CompletedHours,
        	Cour_Title,
        	Cour_Subject,
        	Cour_Grade,
        	Cour_CourseTime,
        	Cour_CoursePlace,
        	Cour_Remark,
        	Cour_UserFee,
        	Cour_TeacherFee 
        FROM
        	tbl_Course 
        WHERE
        	Cour_Id = {}
        '''.format(cid)
        cs.execute(sql)
        data = cs.fetchone()
        dataKeys = ('class','createTime','hours','completedHours','title', 'subject', 'grade', 'courseTime', 'coursePlace', 'remark', 'userFee', 'teacherFee')
        data = list(data)
        data[1] = str(data[1])
        ret['data'] = dict(zip(dataKeys, data))
    return makeRespose(ret)

# 修改拉黑状态
@user.route('/api/backendManage/personnel/user/updateDefriendStatus/<int:id>', methods=['POST'])
def updateDefriendStatus(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        UPDATE tbl_User 
        SET User_DefriendStatus = 1 - User_DefriendStatus 
        WHERE
	        User_Id = {}
        '''.format(id)
        try:
            cs.execute(sql)
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

