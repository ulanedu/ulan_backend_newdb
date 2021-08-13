import flask
from conf.conn import getCursor
from conf.conf import *

order = flask.Blueprint('order',__name__)

# 查询所有订单
@order.route('/api/backendManage/financial/order/getOrders/<int:status>', methods=['GET'])
def getOrders(status):
    ret = retModel.copy()
    studentName = '%'+(flask.request.args.get('studentName')or'')+'%'
    phoneNumber = '%'+(flask.request.args.get('phoneNumber')or'')+'%'
    ret['data']['items'] = []
    page = int(flask.request.args.get('page'))
    perPage = int(flask.request.args.get('perPage'))
    orderDir = flask.request.args.get('orderDir') or 'DESC'
    with getCursor() as cs:
        sql = '''
        SELECT
	        Orde_Id,
	        Orde_Type,
	        Orde_CommodityId,
	        UsIn_StudentName,
	        UsIn_ParentName,
	        UsIn_PhoneNumber,
	        Orde_Amount,
	        Orde_PaymentGateway,
	        Orde_PaymentMethod,
	        Orde_CreateTime,
	        Orde_PaymentTime 
        FROM
	        tbl_Order,
	        tbl_UserInfo 
        WHERE
	        Orde_UserId = UsIn_Id 
	        AND Orde_PaymentStatus = %s 
	        AND UsIn_PhoneNumber LIKE %s 
	        AND UsIn_StudentName LIKE %s 
        ORDER BY
	        Orde_Id
        '''+orderDir
        cs.execute(sql,(status,phoneNumber,studentName))
        data = cs.fetchall()
        dataKeys = ('oid', 'type', 'commodityId', 'studentName', 'parentName', 'phoneNumber', 'amount', 'paymentGateway', 'paymentMethod', 'createTime', 'paymentTime')
        begin = (page-1)*perPage
        end = begin + min(perPage,len(data)-begin)
        for items in data[begin:end]:
            items = list(items)
            items[9] = str(items[9])
            items[10] = str(items[10])
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
        ret['data']['count'] = len(data)
    return makeRespose(ret)

# 查看商品详情
@order.route('/api/backendManage/financial/order/getCommodity/<int:id>', methods=['GET'])
def getCommodity(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        SELECT
	        Orde_Type,
	        Orde_CommodityId 
        FROM
	        tbl_Order 
        WHERE
	        Orde_Id = {}
        '''.format(id)
        cs.execute(sql)
        data = cs.fetchone()
        if data[0] == 'COURSE':
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
            '''.format(data[1])
            cs.execute(sql)
            data = cs.fetchone()
            dataKeys = ('class','createTime','hours','completedHours','title', 'subject', 'grade', 'courseTime', 'coursePlace', 'remark', 'userFee', 'teacherFee')
            data = list(data)
            data[1] = str(data[1])
            ret['data'] = dict(zip(dataKeys, data))
        else:
            ret['msg'] = '订单类型不存在'
            ret['code'] = -1
            return makeRespose(ret)
    return makeRespose(ret)

# 修改支付状态
@order.route('/api/backendManage/financial/order/updatePaymentStatus/<int:id>', methods=['POST'])
def updateDefriendStatus(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        UPDATE tbl_Order 
        SET User_PaymentStatus = 1 - User_PaymentStatus 
        WHERE
	        Orde_Id = {}
        '''.format(id)
        cs.execute(sql)
        ret['msg'] = '操作成功'
        
    return makeRespose(ret)