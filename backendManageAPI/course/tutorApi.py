import flask
from conf.conf import *
from conf.conn import getCursor

tutor = flask.Blueprint("tutor", __name__)

# 新增课程
@tutor.route('/api/backendManage/course/tutor/createCourse', methods=['POST'])
def createCourse():
    ret = retModel.copy()
    params = flask.request.get_json()
    if params['class'] == '预约课':
        params['status'] = 1
    elif params['class'] == '订单课':
        params['status'] = 0
    with getCursor() as cs:
        sql = '''
        SELECT
	        UsIn_Id 
        FROM
	        tbl_UserInfo 
        WHERE
	        UsIn_PhoneNumber = {}
        '''.format(params['userPhoneNumb'])
        cs.execute(sql)
        data = cs.fetchone()
        if data:
            params['userId'] = data[0]
        else:
            raise Exception('用户信息异常')
        sql = '''
        SELECT
	        TeRe_Id 
        FROM
	        tbl_TeacherResume 
        WHERE
	        TeRe_PhoneNumber = {}
        '''.format(params['teacherPhoneNumb'])
        cs.execute(sql)
        data = cs.fetchone()
        if data:
            params['teacherId'] = data[0]
        else:
            if params['status'] == 1:
                raise Exception('教员信息异常')
            params['teacherId'] = -1
        sql = '''
        INSERT INTO tbl_Course ( Cour_Class, Cour_TeacherId, Cour_Status, Cour_Title, Cour_Subject, Cour_Grade, Cour_Remark, Cour_UserFee, Cour_TeacherFee, Cour_Hours, Cour_ShowStatus, Cour_CourseTime, Cour_CoursePlace )
        VALUES
	        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        cs.execute(sql,(params['class'],params['teacherId'],params['status'],params['title'],params['subject'],params['grade'],params['remark'],int(params['userFee']),int(params['teacherFee']),int(params['hours']),int(params['showStatus']),params['courseTime'],params['coursePlace']))
        courseId = cs.lastrowid
        sql = '''
        INSERT INTO tbl_CourseUser ( CoUs_CourseId, CoUs_UserId, CoUs_Status )
        VALUES
        	(%s,%s,1)
        '''
        cs.execute(sql,(int(courseId),int(params['userId'])))
        if params['class'] == '预约课':
            sql = '''
            INSERT INTO tbl_CourseTeacher ( CoTe_CourseId, CoTe_TeacherId )
        VALUES
	        (%s,%s)
            '''
            cs.execute(sql,(int(courseId),int(params['teacherId'])))
        sql = '''
        INSERT INTO tbl_Order ( Orde_Type, Orde_CommodityId, Orde_UserId, Orde_Amount )
        VALUES
	        ('COURSE',%s,%s,%s)
        '''
        cs.execute(sql,(courseId,int(params['userId']),int(params['userFee'])*int(params['hours'])))
    return makeRespose(ret)

# 通过手机号查询用户基本信息
@tutor.route('/api/backendManage/course/tutor/getUserInfo/<int:phoneNumber>',methods=['GET'])
def getUserInfo(phoneNumber):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        SELECT
            UsIn_Id,
            UsIn_StudentName,
            UsIn_StudentSex,
            UsIn_StudentSchool,
            UsIn_StudentGrade,
            UsIn_ParentName
        FROM
            tbl_UserInfo
        WHERE
            UsIn_PhoneNumber = {}
        '''.format(phoneNumber)
        cs.execute(sql)
        data = cs.fetchone()
        dataKeys = ('uid', 'studentName', 'studentSex', 'studentSchool', 'studentGrade', 'parentName')
        ret['data'] = dict(zip(dataKeys, data))
    return makeRespose(ret)

# 通过手机号查看教员信息
@tutor.route('/api/backendManage/course/tutor/getTeacherInfo/<int:phoneNumber>', methods = ['GET'])
def getTeacherInfo(phoneNumber):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        SELECT
        	* 
        FROM
        	tbl_TeacherResume 
        WHERE
        	TeRe_PhoneNumber = {}
        '''.format(phoneNumber)
        cs.execute(sql)
        data = cs.fetchone()
        dataKeys=('tid','tname','tsex','tnation','tpolitics','temail','tgoodSubjects','thobby','tschool','tmajor','tgrade','honours','teachExperience','selfEvaluation','freeTime','avatarURL','tphoneNumber')
        ret['data']=dict(zip(dataKeys, data))
    return makeRespose(ret)

# 获取各个阶段的所有课程基本信息
@tutor.route('/api/backendManage/course/tutor/getCourses/<int:status>',methods=['GET'])
def getCourses(status):
    ret = retModel.copy()
    ret['data']['items'] = []
    studentName = '%'+(flask.request.args.get('studentName')or'')+'%'
    userPhoneNumber = '%'+(flask.request.args.get('userPhoneNumber')or'')+'%'
    teacherName = '%'+(flask.request.args.get('teacherName')or'')+'%'
    teacherPhoneNumber = '%'+(flask.request.args.get('teacherPhoneNumber')or'')+'%'
    orderDir = flask.request.args.get('orderDir') or 'DESC'
    page = int(flask.request.args.get('page'))
    perPage = int(flask.request.args.get('perPage'))
    with getCursor() as cs:
        if status == 0:
            sql = '''
            SELECT
	            Cour_Id,
	            Cour_Class,
	            UsIn_StudentName,
	            UsIn_PhoneNumber,
	            Cour_CreateTime,
                Cour_Title,
	            Cour_Subject,
	            Cour_Grade,
                Cour_Hours,
                Cour_ShowStatus,
	            tbl_CourseTeacherChildren.CoTe_TeacherCount 
            FROM
            	tbl_Course
            	LEFT OUTER JOIN ( SELECT CoTe_CourseId, COUNT( CoTe_TeacherId ) AS CoTe_TeacherCount FROM tbl_CourseTeacher GROUP BY CoTe_CourseId ) AS tbl_CourseTeacherChildren ON tbl_Course.Cour_Id = tbl_CourseTeacherChildren.CoTe_CourseId,
            	tbl_CourseUser,
            	tbl_UserInfo 
            WHERE
                tbl_Course.Cour_DeleteStatus = 0
                AND Cour_Status = 0
            	AND Cour_Id = CoUs_CourseId
            	AND CoUs_UserId = UsIn_Id
                AND UsIn_StudentName LIKE %s
                AND UsIn_PhoneNumber LIKE %s
            ORDER BY
            	Cour_Id
            '''+orderDir
            cs.execute(sql,(studentName,userPhoneNumber))
            data = cs.fetchall()
            dataKeys = ('cid', 'class', 'studentName', 'userPhoneNumber', 'createTime', 'title', 'subject', 'grade', 'hours', 'showStatus', 'teacherCount')
        else:
            sql = '''
            SELECT
            	Cour_Id,
            	Cour_Class,
            	UsIn_StudentName,
            	UsIn_PhoneNumber,
                Cour_CreateTime,
            	TeRe_Name,
            	TeRe_PhoneNumber,
                Cour_Title,
            	Cour_Subject,
            	Cour_Grade,
            	Cour_Hours,
            	Cour_CompletedHours
            FROM
            	tbl_Course,
            	tbl_UserInfo,
            	tbl_CourseUser,
            	tbl_TeacherResume 
            WHERE
            	Cour_Id = CoUs_CourseId 
            	AND CoUs_UserId = UsIn_Id 
            	AND Cour_TeacherId = TeRe_Id 
            	AND Cour_DeleteStatus = 0 
            	AND Cour_Status = %s
                AND UsIn_StudentName LIKE %s
                AND UsIn_PhoneNumber LIKE %s
                AND TeRe_Name LIKE %s
                AND TeRe_PhoneNumber LIKE %s
            ORDER BY
            	Cour_Id
            '''+orderDir
            cs.execute(sql,(status,studentName,userPhoneNumber,teacherName,teacherPhoneNumber))
            data = cs.fetchall()
            dataKeys = ('cid', 'class', 'studentName', 'userPhoneNumber', 'createTime', 'teacherName', 'teacherPhoneNumber', 'title', 'subject', 'grade', 'hours', 'completedHours')
        begin = (page-1)*perPage
        end = begin + min(perPage,len(data)-begin)
        for items in data[begin:end]:
            items = list(items)
            items[4] = str(items[4])
            ret['data']['items'].append(
                dict(zip(dataKeys, items))
            )
        ret['data']['count'] = len(data)
    return makeRespose(ret)

# 获取已删除课程
@tutor.route('/api/backendManage/course/tutor/getDeletedCourses',methods=['GET'])
def getDeletedCourses():
    ret = retModel.copy()
    ret['data']['items'] = []
    page = int(flask.request.args.get('page'))
    perPage = int(flask.request.args.get('perPage'))
    with getCursor() as cs:
        sql = '''
        SELECT
	        Cour_Id,
	        Cour_Class,
	        UsIn_StudentName,
	        UsIn_PhoneNumber,
	        Cour_CreateTime,
            Cour_Title,
	        Cour_Subject,
	        Cour_Grade,
            Cour_Hours 
        FROM
        	tbl_Course,
        	tbl_CourseUser,
        	tbl_UserInfo 
        WHERE
            Cour_DeleteStatus = 1
        	AND Cour_Id = CoUs_CourseId
        	AND CoUs_UserId = UsIn_Id
        ORDER BY
        	Cour_Id DESC
        '''
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('cid', 'class', 'studentName', 'phoneNumber', 'createTime', 'title', 'subject', 'grade', 'hours')
        begin = (page-1)*perPage
        end = begin + min(perPage,len(data)-begin)
        for items in data[begin:end]:
            items = list(items)
            items[4] = str(items[4])
            ret['data']['items'].append(
                dict(zip(dataKeys, items))
            )
        ret['data']['count'] = len(data)
    return makeRespose(ret)

# 获取单个课程的详细信息
@tutor.route('/api/backendManage/course/tutor/getCourse/<int:id>',methods=['GET'])
def getCourse(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        SELECT
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
        '''.format(id)
        cs.execute(sql)
        data = cs.fetchone()
        dataKeys = ('title', 'subject', 'grade', 'courseTime', 'coursePlace', 'remark', 'userFee', 'teacherFee')
        ret['data'] = dict(zip(dataKeys, data))
    return makeRespose(ret)

# 获取投递列表
@tutor.route('/api/backendManage/course/tutor/getCoursTeacher/<int:id>', methods = ['GET'])
def getCourseTeacher(id):
    ret = retModel.copy()
    ret['data']['items'] = []
    with getCursor() as cs:
        sql = '''
        SELECT
        	CoTe_TeacherId,
        	TeRe_Name,
        	TeRe_PhoneNumber,
        	CoTe_Status 
        FROM
        	tbl_CourseTeacher,
        	tbl_TeacherResume 
        WHERE
        	CoTe_TeacherId = TeRe_Id 
        	AND CoTe_CourseId = {}
        '''.format(id)
        cs.execute(sql)
        data = cs.fetchall()
        dataKeys = ('tid', 'name', 'phoneNumber', 'status')
        for items in data:
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
    return makeRespose(ret)

# 查看教员简历
@tutor.route('/api/backendManage/course/tutor/getTeacherResume/<int:id>', methods = ['GET'])
def getTeacherResume(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        SELECT
        	* 
        FROM
        	tbl_TeacherResume 
        WHERE
        	TeRe_Id = %s
        '''
        cs.execute(sql,id)
        data = cs.fetchone()
        dataKeys=('tid','name','sex','nation','politics','email','goodSubjects','hobby','school','major','grade','honours','teachExperience','selfEvaluation','freeTime','avatarURL','phoneNumber')
        ret['data']=dict(zip(dataKeys, data))
    return makeRespose(ret)

# 为课程分配教员
@tutor.route('/api/backendManage/course/tutor/assignTeacher/<int:cid>/<int:tid>', methods=['POST'])
def assignTeacher(cid,tid):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        UPDATE tbl_Course 
        SET Cour_TeacherId = %s,
        Cour_Status = 1 
        WHERE
        	Cour_Id = %s
        '''
        try:
            cs.execute(sql,(tid,cid))
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 修改课程(订单)信息
@tutor.route('/api/backendManage/course/tutor/updateCourse/<int:id>', methods=['POST'])
def updateCourse(id):
    ret = retModel.copy()
    params = flask.request.get_json()
    with getCursor() as cs:
        sql1 = '''
        UPDATE tbl_Course 
        SET Cour_Title = %s,
        Cour_Subject = %s,
        Cour_Grade = %s,
        Cour_Remark = %s,
        Cour_UserFee = %s,
        Cour_TeacherFee = %s,
        Cour_Hours = %s,
        Cour_CourseTime = %s,
        Cour_CoursePlace = %s
        WHERE
        	Cour_Id = %s
        '''
        sql2 = '''
        UPDATE tbl_Order 
        SET Orde_Amount = %s 
        WHERE
        	Orde_CommodityId = %s
        '''
        try:
            cs.execute(sql1,(params['title'],params['subject'],params['grade'],params['remark'],params['userFee'],params['teacherFee'],params['hours'],params['courseTime'],params['coursePlace'],id))
            cs.execute(sql2,(int(params['hours'])*int(params['userFee']),id))
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 快速修改展示状态
@tutor.route('/api/backendManage/course/tutor/updateCourseShowStatus/<int:id>', methods=['POST'])
def updateCourseShowStatus(id):
    ret = retModel.copy()
    params = flask.request.get_json()
    with getCursor() as cs:
        sql = '''
        UPDATE tbl_Course 
        SET Cour_ShowStatus = %s
        WHERE
        	Cour_Id = %s
        '''
        try:
            cs.execute(sql,(params['showStatus'],id))
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 删除课程(订单)
@tutor.route('/api/backendManage/course/tutor/deleteCourse/<int:id>', methods=['POST'])
def deleteCourse(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql1 = '''
        UPDATE tbl_Course 
        SET Cour_DeleteStatus = 1 
        WHERE
        	Cour_Id = {}
        '''.format(id)
        sql2 = '''
        DELETE 
        FROM
        	tbl_Order 
        WHERE
        	Orde_CommodityId = {}
        '''.format(id)
        try:
            cs.execute(sql1)
            cs.execute(sql2)
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 恢复课程(订单)
@tutor.route('/api/backendManage/course/tutor/restoreCourse/<int:id>', methods=['POST'])
def restoreCourse(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql1 = '''
        UPDATE tbl_Course 
        SET Cour_DeleteStatus = 0 
        WHERE
        	Cour_Id = {}
        '''.format(id)
        sql2 = '''
        INSERT INTO tbl_Order ( Orde_Type, Orde_CommodityId, Orde_UserId, Orde_Amount )
        VALUES
        	( 'COURSE',%s,
        	( SELECT CoUs_UserId FROM tbl_CourseUser WHERE CoUs_CourseId = %s ),
        	( SELECT Cour_Hours * Cour_UserFee FROM tbl_Course WHERE Cour_Id = %s ))
        '''
        try:
            cs.execute(sql1)
            cs.execute(sql2,(id,id,id))
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 彻底删除课程(订单)
@tutor.route('/api/backendManage/course/tutor/deleteCoursePermanent/<int:id>', methods=['POST'])
def deleteCoursePermanent(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        DELETE FROM tbl_Course 
        WHERE
        	Cour_Id = {};
        '''.format(id)
        try:
            cs.execute(sql)
            ret['msg'] = '操作成功'
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)

# 结课
@tutor.route('/api/backendManage/course/tutor/endCourse/<int:id>', methods=['POST'])
def endCourse(id):
    ret = retModel.copy()
    with getCursor() as cs:
        sql = '''
        UPDATE tbl_Course 
        SET Cour_Status = 3 
        WHERE
	        Cour_CompletedHours = Cour_Hours 
	        AND Cour_Id = {}
        '''.format(id)
        try:
            cs.execute(sql)
            rowcount = cs.rowcount
            if rowcount == 1:
                ret['msg'] = '操作成功'
            else:
                raise Exception('课程暂未完成')
        except Exception as e:
            ret['msg'] = str(e)
            ret['code'] = -1
    return makeRespose(ret)