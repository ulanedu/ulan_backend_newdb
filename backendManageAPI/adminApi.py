import flask
import time
import redis
from conf.conn import getCursor
from utils import genMD5
from conf.conf import *

admin = flask.Blueprint("admin", __name__)

# 验证token
@admin.route('/api/backendManage/admin/isVaildToken/<token>', methods=['GET'])
def isVaildToken(token):
    print("rec token:", token)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    re = r.get('token:' + token)
    if (re):
        return makeRespose({"isVaild": True})
    else:
        return makeRespose({"isVaild": False})

# 管理员登录
@admin.route('/api/backendManage/admin/login', methods=['POST'])
def login():
    ret = retModel.copy()
    params = flask.request.get_json()
    username = params['username']
    password = params['password']

    with getCursor() as cs:
        sql = '''
        SELECT Admi_Id
        FROM tbl_Administrator
        WHERE Admi_UserName = %s AND Admi_PassWord = MD5(%s)
        '''
        cs.execute(sql, (username, password))
        data = cs.fetchone()
        if (data):
            token_str = "ulan"+username + "@" + \
                "###-" + "timestamp:" + str(time.time()-123356)
            token = genMD5(token_str)
            ret['msg'] = '登录成功'
            ret['data']['token'] = token
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.set('token:' + token, data[0], ex=3600)
    return makeRespose(ret)

# 管理员登出
@admin.route('/api/backendManage/admin/logout/<token>',methods=['GET'])
def logout(token):
    ret = retModel.copy()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    try:
        r.delete('token'+token)
        ret['msg'] = '操作成功'
    except Exception as e:
        print(e)
        ret['msg'] = str(e)
        ret['code'] = -1
        return makeRespose(ret)
    return makeRespose(ret)

# 获取管理员信息
@admin.route('/api/backendManage/admin/getAdminInfo/<token>', methods=['GET'])
def getAdminInfo(token):
    ret = retModel.copy()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    Id = r.get('token:'+token)
    if (Id):
        with getCursor() as cs:
            sql = '''
            SELECT Admi_PhoneNumber,Admi_Email,Admi_Name,Admi_Sex,Admi_Academy,Admi_AvatarURL
            FROM tbl_Administrator
            WHERE Admi_Id = {}
            '''.format(Id)
            cs.execute(sql)
            data = cs.fetchone()
            dataKeys = ('phonenumber','email','name','sex','academy','avatar')
            ret['data'] = dict(zip(dataKeys, data))
    else:
        ret['code'] = -1
        ret['msg'] = '登录超时,请刷新页面'
    return makeRespose(ret)

# 修改管理员信息
@admin.route('/api/backendManage/admin/updateAdminInfo/<token>', methods=['POST'])
def updateAdminInfo(token):
    ret = retModel.copy()
    params = flask.request.get_json()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    Id = r.get('token:'+token)
    if (Id):
        with getCursor() as cs:
            sql = '''
            UPDATE tbl_Administrator
            SET Admi_PhoneNumber=%s,Admi_Email=%s,Admi_Name=%s,Admi_Sex=%s,Admi_Academy=%s
            WHERE Admi_Id = %s
            '''
            cs.execute(sql,(
                params['phonenumber'],params['email'],params['name'],params['sex'],params['academy'],Id
            ))
            print(params)
            ret['msg'] = '更新成功'
    else:
        ret['code'] = -1
        ret['msg'] = '登录超时'
    return makeRespose(ret)

# 修改管理员密码
@admin.route('/api/backendManage/admin/updateAdminPassword/<token>', methods=['POST'])
def updateAdminPassword(token):
    ret = retModel.copy()
    params = flask.request.get_json()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    Id = r.get('token:'+token)
    if (Id):
        with getCursor() as cs:
            sql = '''
            SELECT *
            FROM tbl_Administrator
            WHERE Admi_Id = %s AND Admi_PassWord = MD5(%s)
            '''
            cs.execute(sql,(
                Id,params['oldPassword']
            ))
            data = cs.fetchone()
            if (data):
                sql = '''
                UPDATE tbl_Administrator
                SET Admi_PassWord = MD5(%s)
                WHERE Admi_Id = %s AND Admi_PassWord = MD5(%s)
                '''
                cs.execute(sql,(
                    params['password'],Id,params['oldPassword']
                ))
                ret['msg'] = '更新成功'
            else:
                ret['code'] = -1
                ret['msg'] = '旧密码不正确'
    else:
        ret['code'] = -1
        ret['msg'] = '登录超时'
    return makeRespose(ret)

# 上传头像
@admin.route('/api/backendManage/admin/uploadImg', methods=['GET','POST','OPTIONS'])
def uploadImg():
    ret = retModel.copy()
    img = flask.request.files.get('file')
    path = "../static/"
    img.save(path)
    print(path)
    ret['data']['file_path'] = path
     # 获取图片文件
    # img = flask.request.form.get('file')
    # # path = "/static/img/"
    # print(img)
    # 图片名称
    # img_name = img.filename
    # 图片path和名称组成图片的保存路径
    # file_path = path + img_name
    # 保存图片
    # img.save(file_path)
    # print(img_name)
    return makeRespose(ret)