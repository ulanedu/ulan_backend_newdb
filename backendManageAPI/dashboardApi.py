import flask
from conf.conn import getCursor
from conf.conf import *
import numpy as np

dashboard = flask.Blueprint("dashboard", __name__)

# 获取主页信息
@dashboard.route('/api/backendManage/dashboard/getData',methods = ['GET'])
def getData():
    ret = retModel.copy()
    data = []
    with getCursor() as cs:
        sql = [
            '''SELECT COUNT(User_Id) FROM tbl_User''',
            '''SELECT COUNT(Teac_Id) From tbl_Teacher''',
            '''SELECT SUM(Orde_Amount) From tbl_Order WHERE Orde_PaymentStatus = 1''',
            '''SELECT SUM(PaRe_Amount) From tbl_PayrollRecord''',
            '''SELECT COUNT(*) FROM tbl_Course WHERE Cour_Status = 0''',
            '''SELECT COUNT(*) FROM tbl_Course WHERE Cour_Class = \'预约课\' AND Cour_Status = 1''',
            '''SELECT COUNT(*) FROM tbl_Course WHERE Cour_Status = 2''',
            '''SELECT COUNT(*) FROM tbl_DismissalApplication WHERE DiAp_AdminReviewStatus = 0'''
        ]
        for i in range(len(sql)):
            cs.execute(sql[i])
            item = list(cs.fetchone())[0]
            if item:
                data.append(str(item))
            else:
                data.append(0)
        dataKeys = ('userCount','teacherCount','totalRevenue','totalExpenses','assignedCourses','reserveCourses','ongoingCourses','dismissCourses')
        ret['data'] = dict(zip(dataKeys, data))
    return makeRespose(ret)

# 获取收支明细
@dashboard.route('/api/backendManage/dashboard/getDetail',methods = ['GET'])
def getDetail():
    ret = retModel.copy()
    startDate = flask.request.args.get('startDate')
    endDate = flask.request.args.get('endDate')
    page = int(flask.request.args.get('page'))
    perPage = int(flask.request.args.get('perPage'))
    data = []
    ret['data']['items'] = []
    with getCursor() as cs:
        if startDate and endDate:
            sql = [
                '''SELECT DATE_FORMAT(Orde_PaymentTime,\'%%Y-%%m-%%d\') days, SUM(Orde_Amount) FROM tbl_Order WHERE Orde_PaymentStatus = 1 AND (Orde_PaymentTime BETWEEN %s AND %s) GROUP BY days ORDER BY Orde_PaymentTime DESC''',
                '''SELECT DATE_FORMAT(PaRe_Time,\'%%Y-%%m-%%d\') days, SUM(PaRe_Amount) FROM tbl_PayrollRecord WHERE PaRe_Time BETWEEN %s AND %s GROUP BY days ORDER BY PaRe_Time DESC''',
                '''SELECT DATE_FORMAT(User_CreateTime,\'%%Y-%%m-%%d\') days, COUNT(User_Id) FROM tbl_User WHERE User_CreateTime BETWEEN %s AND %s GROUP BY days ORDER BY User_CreateTime DESC''',
                '''SELECT DATE_FORMAT(Orde_CreateTime,\'%%Y-%%m-%%d\') days, COUNT(Orde_Id) FROM tbl_Order WHERE Orde_CreateTime BETWEEN %s AND %s GROUP BY days ORDER BY Orde_CreateTime DESC'''
            ]
            for i in range(len(sql)):
                cs.execute(sql[i],(startDate,endDate))
                data.append(cs.fetchall())
        else:
            sql = [
                '''SELECT DATE_FORMAT(Orde_PaymentTime,\'%Y-%m-%d\') days, SUM(Orde_Amount) FROM tbl_Order WHERE Orde_PaymentStatus = 1 GROUP BY days ORDER BY Orde_PaymentTime DESC''',
                '''SELECT DATE_FORMAT(PaRe_Time,\'%Y-%m-%d\') days, SUM(PaRe_Amount) FROM tbl_PayrollRecord GROUP BY days ORDER BY PaRe_Time DESC''',
                '''SELECT DATE_FORMAT(User_CreateTime,\'%Y-%m-%d\') days, COUNT(User_Id) FROM tbl_User GROUP BY days ORDER BY User_CreateTime DESC''',
                '''SELECT DATE_FORMAT(Orde_CreateTime,\'%Y-%m-%d\') days, COUNT(Orde_Id) FROM tbl_Order GROUP BY days ORDER BY Orde_CreateTime DESC'''
            ]
            for i in range(len(sql)):
                cs.execute(sql[i])
                data.append(cs.fetchall())
        lenth = [len(data[0]),len(data[1]),len(data[2]),len(data[3])]
        foreach = [0,0,0,0]
        k = 0
        while sum(foreach) < sum(lenth):
            maxDate = '0000-00-00'
            for i in range(4):
                if foreach[i] < lenth[i] and str(data[i][foreach[i]][0]) > maxDate:
                    maxDate = str(data[i][foreach[i]][0])
            ret['data']['items'].append([maxDate,0,0,0,0])
            for i in range(4):
                if foreach[i] < lenth[i] and str(data[i][foreach[i]][0]) == maxDate:
                    ret['data']['items'][k][i+1] = str(data[i][foreach[i]][1])
                    foreach[i] += 1
            k += 1
        dataKeys=('date','dailyincome','dailypay','dailyuser','dailyorder')
        data = ret['data']['items']
        ret['data']['items'] = []
        begin = (page-1)*perPage
        end = begin + min(perPage,len(data)-begin)
        for items in data[begin:end]:
            ret['data']['items'].append(
                dict(zip(dataKeys,items))
            )
        ret['data']['count'] = len(data)
        data = np.array(data)
        ret['data']['date'] = list(reversed(list(data[:,0])))
        ret['data']['dailyincome'] = list(reversed(list(data[:,1])))
        ret['data']['dailypay'] = list(reversed(list(data[:,2])))
        ret['data']['dailyuser'] = list(reversed(list(data[:,3])))
        ret['data']['dailyorder'] = list(reversed(list(data[:,4])))
    return makeRespose(ret)