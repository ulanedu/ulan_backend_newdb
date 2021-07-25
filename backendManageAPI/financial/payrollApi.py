import flask
from conf.conn import getCursor
from conf.conf import *
import redis

ulanpayroll = flask.Blueprint('ulanpayroll',__name__)

# 查询工资发放记录
@ulanpayroll.route('/api/backendManage/financial/payroll/getPayrollRecords', methods=['GET'])
def getPayrollRecords():
    ret = retModel.copy()
    ret['data']['items'] = []
    startDate = (flask.request.args.get('dateRange[0]') or '0000-01-01') + ' 00:00:00'
    endDate = (flask.request.args.get('dateRange[1]') or '9999-12-31') + ' 23:59:59'
    print(startDate)
    print(endDate)
    with getCursor() as cs:
        sql = '''
        SELECT
	        PaRe_Id,
	        PaRe_SubjectClass,
	        tbl_Administrator.Admi_Name,
	        tbl_Administrator.Admi_PhoneNumber,
	        TeRe_Name,
	        TeRe_PhoneNumber,
	        PaRe_Time,
	        PaRe_Amount,
	        tbl_AdmiPlus.Admi_Name,
	        PaRe_Remark 
        FROM
	        tbl_PayrollRecord,
	        tbl_TeacherResume,
	        tbl_Administrator,
	        tbl_Administrator AS tbl_AdmiPlus 
        WHERE
	        tbl_Administrator.Admi_Id = PaRe_SubjectId *(
		        1-PaRe_SubjectClass 
	        ) 
	        OR TeRe_Id = PaRe_SubjectId * PaRe_SubjectClass 
	        AND PaRe_AdminId = tbl_AdmiPlus.Admi_Id 
        GROUP BY
	        PaRe_Id 
        HAVING
	        PaRe_Time BETWEEN %s 
	        AND %s;
        '''
        cs.execute(sql,(startDate,endDate))
        data = cs.fetchall()
        dataKeys = ('prid', 'subjectClass', 'adminName', 'adminPhoneNumber', 'teacherName', 'teacherPhoneNumber', 'time', 'amount', 'aName', 'remark')
        for items in data:
            items = list(items)
            items[6] = str(items[6])
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
    return makeRespose(ret)

# 查询记录详情
@ulanpayroll.route('/api/backendManage/financial/payroll/getPayrollDetail/<int:id>', methods=['GET'])
def getPayrollDetail(id):
    ret = retModel.copy()
    ret['data']['items'] = []
    with getCursor() as cs:
        sql = '''
        SELECT
	        DiAp_Id,
	        Cour_Title,
	        DiAp_DismissedHour,
	        Cour_TeacherFee,
	        DiAp_AdminReviewTime,
	        Admi_Name,
	        DiAp_DismissedHour * Cour_TeacherFee 
        FROM
	        tbl_DismissalApplication,
	        tbl_Course,
	        tbl_Administrator 
        WHERE
	        DiAp_CourseId = Cour_Id 
	        AND DiAp_AdminId = Admi_Id 
	        AND DiAp_PayrollRecordId = {}
        '''.format(id)
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('daid', 'title', 'dismissedHour', 'teacherFee', 'adminReviewTime', 'adminName', 'amount')
        for items in data:
            items = list(items)
            items[4] = str(items[4])
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
    return makeRespose(ret)

# 查询可发放工资
@ulanpayroll.route('/api/backendManage/financial/payroll/getPayrolls', methods = ['GET'])
def getPayrolls():
    ret = retModel.copy()
    ret['data']['items'] = []
    with getCursor() as cs:
        sql = '''
        SELECT
	        TeRe_Id,
	        TeRe_Name,
	        TeRe_School,
	        TeRe_Major,
	        TeRe_Grade,
	        TeRe_PhoneNumber,
	        SUM( Cour_TeacherFee * DiAp_DismissedHour ) 
        FROM
	        tbl_DismissalApplication,
	        tbl_TeacherResume,
	        tbl_Course 
        WHERE
	        DiAp_CourseId = Cour_Id 
	        AND Cour_TeacherId = TeRe_Id 
	        AND DiAp_AdminReviewStatus = 1 
	        AND DiAp_PayrollRecordId = - 1 
        GROUP BY
	        TeRe_Id
        '''
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('sid', 'name','school','major','grade', 'phoneNumber', 'amount')
        for items in data:
            items = list(items)
            items[6] = str(items[6])
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
        print(ret)
    return makeRespose(ret)

# 查询可发放工资详情
@ulanpayroll.route('/api/backendManage/financial/payroll/getBeforePayrollDetail/<int:tid>', methods=['GET'])
def getBeforePayrollDetail(tid):
    ret = retModel.copy()
    ret['data']['items'] = []
    with getCursor() as cs:
        sql = '''
        SELECT
	        DiAp_Id,
	        Cour_Title,
	        DiAp_DismissedHour,
	        Cour_TeacherFee,
	        DiAp_AdminReviewTime,
	        Admi_Name,
	        DiAp_DismissedHour * Cour_TeacherFee 
        FROM
	        tbl_DismissalApplication,
	        tbl_Course,
	        tbl_Administrator 
        WHERE
	        DiAp_CourseId = Cour_Id 
	        AND DiAp_AdminId = Admi_Id 
	        AND DiAp_PayrollRecordId = - 1 
	        AND DiAp_AdminReviewStatus = 1 
	        AND Cour_TeacherId = {}
        '''.format(tid)
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('daid', 'title', 'dismissedHour', 'teacherFee', 'adminReviewTime', 'adminName', 'amount')
        for items in data:
            items = list(items)
            items[4] = str(items[4])
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
    return makeRespose(ret)

# 发放工资
@ulanpayroll.route('/api/backendManage/financial/payroll/payroll/<token>/<int:sjclass>', methods=['POST'])
def payroll(token,sjclass):
    ret = retModel.copy()
    params = flask.request.get_json()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    aid = r.get('token:'+token)
    with getCursor() as cs:
        try:
            if sjclass == 1:
                sql = '''
                INSERT INTO tbl_PayrollRecord ( PaRe_SubjectClass, PaRe_SubjectId, PaRe_AdminId, PaRe_Amount )
                VALUES
	                (%s,%s,%s,%s)
                '''
                cs.execute(sql,(sjclass,params['sid'],aid,params['amount']))
                lastrowId = cs.lastrowid
                sql = '''
                UPDATE tbl_DismissalApplication 
                SET DiAp_PayrollRecordId = %s 
                WHERE
	                DiAp_CourseId IN ( SELECT Cour_Id FROM tbl_Course WHERE Cour_TeacherId = %s ) 
	                AND DiAp_AdminReviewStatus = 1 
	                AND DiAp_PayrollRecordId = -1
                '''
                cs.execute(sql,(lastrowId,params['sid']))
            elif sjclass == 0:
                sql = '''
                INSERT INTO tbl_PayrollRecord ( PaRe_SubjectClass, PaRe_SubjectId, PaRe_AdminId, PaRe_Amount, PaRe_Remark )
                VALUES
	                (%s,%s,%s,%s,%s)
                '''
                cs.execute(sql,(sjclass,params['adminId'],aid,params['amount'],params['remark']))
            ret['msg'] = '发放成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 快速编辑备注
@ulanpayroll.route('/api/backendManage/financial/payroll/updateRemark', methods=['POST'])
def updateRemark():
    ret = retModel.copy()
    params = flask.request.get_json()
    print(params)
    with getCursor() as cs:
        try:
            sql = '''
            UPDATE tbl_PayrollRecord 
            SET PaRe_Remark = %s 
            WHERE
	            PaRe_Id = %s
            '''
            cs.execute(sql,(params['remark'],params['prid']))
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 查所有Options
@ulanpayroll.route('/api/backendManage/financial/payroll/getOptions', methods=['GET'])
def getOptions():
    ret = retModel.copy()
    ret['data']['Admins'] = []
    with getCursor() as cs:
        sql = '''
        SELECT Admi_Id, Admi_Name, Admi_PhoneNumber
        FROM tbl_Administrator
        '''
        try:
            dataKeys = ('label','value')
            cs.execute(sql)
            data = cs.fetchall()
            for items in data:
                ret['data']['Admins'].append(
                    dict(zip(dataKeys,(items[1]+'：'+items[2],items[0])))
                )
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)