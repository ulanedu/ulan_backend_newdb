from flask import Flask, request
from flask_cors import CORS
# from v2 import orderApi, courseApi, teacherApi, authApi, resumesApi
# from wechatAppAPI_v1 import wx_studentApi, wx_teacherApi, wx_commonApi
from backendManageAPI import adminApi, dashboardApi
from backendManageAPI.course import tutorApi, dismissalApi
from backendManageAPI.personnel import teacherApi,userApi
from backendManageAPI.financial import orderApi,payrollApi

app = Flask(__name__)
CORS(app, resources=r'/*')
app.secret_key = '@KJHKJDSH&@^&!@###ULANEDU'

app.register_blueprint(adminApi.admin)
app.register_blueprint(dashboardApi.dashboard)

app.register_blueprint(tutorApi.tutor)
app.register_blueprint(dismissalApi.dismiss)

app.register_blueprint(teacherApi.teacher)
app.register_blueprint(userApi.user)

app.register_blueprint(orderApi.order)
app.register_blueprint(payrollApi.ulanpayroll)


# @app.before_request
# def beforeRequest():
#     headers = request.headers
#     print(request.url_rule)
#     print(headers)
#     return "401", 401


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='172.27.0.16')
