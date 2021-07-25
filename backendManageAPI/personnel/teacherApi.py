import flask
import redis
from conf.conn import getCursor
from conf.conf import *

teacher = flask.Blueprint('teacher',__name__)

# 查看所有师资
@teacher.route('/api/backendManage/personnel/teacher/getTeachers/<int:status>',methods=['GET'])
def getTeachers(status):
    ret = retModel.copy()
    ret['data']['items'] = []
    name = '%'+(flask.request.args.get('name')or'')+'%'
    phoneNumber = '%'+(flask.request.args.get('phoneNumber')or'')+'%'
    page = int(flask.request.args.get('page'))
    perPage = int(flask.request.args.get('perPage'))
    orderDir = flask.request.args.get('orderDir') or 'ASC'
    with getCursor() as cs:
        sql = '''
        SELECT
	        Teac_Id,
	        TeRe_Name,
	        TeRe_PhoneNumber,
	        TeRe_GoodSubjects,
	        TeRe_School,
	        TeRe_Major,
	        TeRe_Grade 
        FROM
	        tbl_Teacher,
	        tbl_TeacherResume 
        WHERE
	        Teac_Id = TeRe_Id 
	        AND Teac_ContractStatus = % s 
	        AND TeRe_Name LIKE % s 
	        AND TeRe_PhoneNumber LIKE % s 
        ORDER BY
	        TeAc_Id
        '''+orderDir
        cs.execute(sql,(status,name,phoneNumber))
        data = cs.fetchall()
        dataKeys = ('tid', 'name', 'phoneNumber', 'goodSubjects', 'school', 'major', 'grade')
        ret['data']['count'] = len(data)
        begin = (page-1)*perPage
        end = begin + min(perPage,len(data)-begin)
        for items in data[begin:end]:
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
    return makeRespose(ret)

# 查看教员简历
@teacher.route('/api/backendManage/personnel/getTeacherResume/<int:id>', methods=['GET'])
def getTeacherResume(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        SELECT
	        * 
        FROM
	        tbl_TeacherResume 
        WHERE
	        TeRe_Id = {}
        '''.format(id)
        cs.execute(sql)
        data = cs.fetchone()
        dataKeys = ('id','name','sex','nation','politicalStatus','email','goodSubjects','hobby','school','major','grade','honours','teachExperience','selfEvaluation','freeTime','avatarURL','phoneNumber')
        ret['data'] = dict(zip(dataKeys,data))
    return makeRespose(ret)

# 查看教员评价
@teacher.route('/api/backendManage/personnel/getTeacherEvaluation/<int:tid>', methods=['GET'])
def getTeacherEvalustion(tid):
    ret = retModel.copy()
    ret['data']['items'] = []
    with getCursor() as cs:
        sql = '''
        SELECT
	        TeEv_Id,
	        Admi_Name,
	        TeEv_Content,
	        TeEv_Time 
        FROM
	        tbl_TeacherEvaluation,
	        tbl_Administrator 
        WHERE
	        TeEv_AdminId = Admi_Id 
	        AND TeEv_TeacherId = {} 
        ORDER BY
	        TeEv_Id DESC
        '''.format(tid)
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('teid', 'adminName', 'content', 'time')
        for items in data:
            items = list(items)
            items[3] = str(items[3])
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
    return makeRespose(ret)

# 评价教员
@teacher.route('/api/backendManage/personnel/evaluateTeacher/<int:tid>/<token>', methods=['POST'])
def evaluateTeacher(tid,token):
    ret = retModel.copy()
    params = flask.request.get_json()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    aid = r.get('token:'+token)
    with getCursor() as cs:
        sql = '''
        INSERT INTO tbl_TeacherEvaluation ( TeEv_AdminId, TeEv_TeacherId, TeEv_Content )
        VALUES
	        (%s,%s,%s)
        '''
        try:
            cs.execute(sql,(aid,tid,params['content']))
            ret['msg'] = '评价成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 删除评价
@teacher.route('/api/backendManage/personnel/deleteTeacherEvaluation/<int:teid>', methods=['POST'])
def deleteTeacherEvaluationr(teid):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        DELETE 
        FROM
	        tbl_TeacherEvaluation 
        WHERE
	        TeEv_Id = {}
        '''.format(teid)
        cs.execute(sql)
    return makeRespose(ret)

# 签约(解除合约)
@teacher.route('/api/backendManage/personnel/updateContractStatus/<int:tid>', methods=['POST'])
def updateContractStatus(tid):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        UPDATE tbl_Teacher 
        SET Teac_ContractStatus = 1 - Teac_ContractStatus 
        WHERE
	        Teac_Id = {}
        '''.format(tid)
        try:
            cs.execute(sql)
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)