from flask import make_response
import json

baseURL = "http://youlanedu.com/api/backendManage/"
Origin = 'http://localhost:7050'

retModel = {
    "code": 0,
    "msg": "",
    "data": {},
}

def makeRespose(res, code=200):
    tmp = make_response(json.dumps(res))
    return tmp, code
