import flask
import redis
from conf.conf import *
from conf.conn import getCursor

dismiss = flask.Blueprint("dismiss",__name__)

# 查询各状态的消课申请信息
@dismiss.route('/api/backendManage/course/dismissal/getDismissalCourses/<int:status>', methods=['GET'])
def getDismissalCourses(status):
    ret = retModel.copy()
    ret['data']['items'] = []
    teacherName = '%'+(flask.request.args.get('teacherName')or'')+'%'
    teacherPhoneNumber = '%'+(flask.request.args.get('teacherPhoneNumber')or'')+'%'
    page = int(flask.request.args.get('page'))
    perPage = int(flask.request.args.get('perPage'))
    orderDir = flask.request.args.get('orderDir') or 'ASC'
    with getCursor() as cs:
        if status == 0:
            sql = '''
            SELECT
            	DiAp_Id,
                Cour_Title,
            	TeRe_Name,
                TeRe_PhoneNumber,
            	DiAp_DismissedHour,
            	DiAp_ApplicationTime,
            	DiAp_UserReviewStatus,
            	DiAp_UserReviewTime 
            FROM
            	tbl_DismissalApplication,
            	tbl_Course,
            	tbl_TeacherResume 
            WHERE
            	DiAp_CourseId = Cour_Id 
            	AND Cour_TeacherId = TeRe_Id 
                AND TeRe_Name LIKE %s
                AND TeRe_PhoneNumber LIKE %s
            	AND DiAp_AdminReviewStatus = %s
            ORDER BY
            	DiAp_Id 
            '''+orderDir
            cs.execute(sql,(teacherName,teacherPhoneNumber,int(status)))
            data = cs.fetchall()
            dataKeys = ('daid','title','teacherName','teacherPhoneNumber','dismissedHour','applicationTime','userReviewStatus','userReviewTime')
        else:
            sql = '''
            SELECT
            	DiAp_Id,
                Cour_Title,
            	TeRe_Name,
                TeRe_PhoneNumber,
            	DiAp_DismissedHour,
            	DiAp_ApplicationTime,
            	DiAp_UserReviewStatus,
            	DiAp_UserReviewTime,
                Admi_Name,
                DiAp_AdminReviewTime,
                DiAp_PayrollRecordId
            FROM
            	tbl_DismissalApplication,
            	tbl_Course,
            	tbl_TeacherResume,
                tbl_Administrator
            WHERE
            	DiAp_CourseId = Cour_Id 
            	AND Cour_TeacherId = TeRe_Id
                AND Admi_Id = DiAp_AdminId
            	AND TeRe_Name LIKE %s
                AND TeRe_PhoneNumber LIKE %s
            	AND DiAp_AdminReviewStatus = %s
            ORDER BY
            	DiAp_Id 
            '''+orderDir
            cs.execute(sql,(teacherName,teacherPhoneNumber,int(status)))
            data = cs.fetchall()
            dataKeys = ('daid','title','teacherName','teacherPhoneNumber','dismissedHour','applicationTime','userReviewStatus','userReviewTime','adminName','adminReviewTime','payrollRecordId')
        begin = (page-1)*perPage
        end = begin + min(perPage,len(data)-begin)
        for items in data[begin:end]:
            items = list(items)
            items[5] = str(items[5])
            items[7] = str(items[7])
            if status > 0:
                items[9] = str(items[9])
            ret['data']['items'].append(
                dict(zip(dataKeys, items))
            )
        ret['data']['count'] = len(data)
    return makeRespose(ret)

# 查看消课申请详情
@dismiss.route('/api/backendManage/course/dismissal/getDismissalCourse/<int:id>', methods=['GET'])
def getDismissalCourse(id):
    ret = retModel.copy()

    with getCursor() as cs:
        sql = '''
        SELECT
        	TeRe_Name,
        	TeRe_PhoneNumber,
        	UsIn_StudentName,
        	UsIn_PhoneNumber,
        	Cour_Subject,
        	Cour_Grade,
        	Cour_Hours,
        	Cour_CompletedHours,
            Cour_UserFee,
            Cour_TeacherFee,
        	Cour_CourseTime,
        	Cour_CoursePlace,
        	DiAp_DismissedHour,
        	DiAp_CourseContent,
        	DiAp_UserEvaluation 
        FROM
        	tbl_DismissalApplication,
        	tbl_Course,
        	tbl_TeacherResume,
        	tbl_CourseUser,
        	tbl_UserInfo 
        WHERE
        	DiAp_CourseId = Cour_Id 
        	AND Cour_TeacherId = TeRe_Id 
        	AND DiAp_CourseId = CoUs_CourseId 
        	AND CoUs_UserId = UsIn_Id 
        	AND DiAp_Id = {}
        '''.format(id)
        cs.execute(sql)
        data = cs.fetchone()
        dataKeys = ('teacherName', 'teacherPhoneNumber', 'studentName', 'studentPhoneNumber', 'subject', 'grade', 'hours', 'completedHours', 'userFee', 'teacherFee', 'courseTime', 'coursePlace', 'dismissedHour', 'courseContent', 'userEvaluation')
        ret['data'] = dict(zip(dataKeys,data))
    return makeRespose(ret)

# 通过申请
@dismiss.route('/api/backendManage/course/dismissal/passApplication/<int:daid>/<token>', methods=['POST'])
def passApplication(daid,token):
    ret = retModel.copy()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    aid = r.get('token:'+token)
    with getCursor() as cs:
        sql = '''
        SELECT
        	DiAp_DismissedHour,
	        DiAp_CourseId 
        FROM
	        tbl_DismissalApplication 
        WHERE
	        DiAp_Id = {}
        '''.format(daid)
        sql1 = '''
        UPDATE tbl_Course 
        SET Cour_CompletedHours = Cour_CompletedHours + %s 
        WHERE
	        Cour_Id = %s
        '''
        sql2 = '''
        UPDATE tbl_DismissalApplication 
        SET DiAp_AdminReviewStatus = 1,
        DiAp_AdminReviewTime = NOW(),
        DiAp_AdminId = %s 
        WHERE
	        DiAp_Id = %s;
        '''
        try:
            cs.execute(sql)
            data = cs.fetchone()
            data = list(data)
            cs.execute(sql1,(data[0],data[1]))
            cs.execute(sql2,(aid,daid))
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1

    return makeRespose(ret)

# 拒绝申请
@dismiss.route('/api/backendManage/course/dismissal/refuseApplication/<int:daid>/<token>', methods=['POST'])
def refuseApplication(daid,token):
    ret = retModel.copy()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    aid = r.get('token:'+token)
    with getCursor() as cs:
        sql = '''
        UPDATE tbl_DismissalApplication 
        SET DiAp_AdminReviewStatus = 2,
        DiAp_AdminReviewTime = NOW(),
        DiAp_AdminId = %s 
        WHERE
	        DiAp_Id = %s
        '''
        try:
            cs.execute(sql,(int(aid),int(daid)))
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
        
    return makeRespose(ret)