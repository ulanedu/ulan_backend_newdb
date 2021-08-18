# 微信接口文档 #

https://api.youlanedu.com/

## common ##

### 【获取验证码】 ###

#### Description ####

向用户手机发送验证码

#### Method URL

POST /api/weChat/common/getCaptcha

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数        | 必选 | 类型   | 说明   |
| ----------- | ---- | ------ | ------ |
| phoneNumber | true | String | 手机号 |

#### Response

| 返回字段 | 字段类型   | 说明     |
| -------- | ---------- | -------- |
| msg      | String     | 请求结果 |
| code     | Int        | 请求状态 |
| data     | Dictionary | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### 调用示例

{

"phoneNumber":"123456789"

}

#### 返回示例

{

"msg" : "success",

"code" : 0,

"data" : {}

}



## user

### 【获取用户各阶段课程】 ###

#### Description ####

获取用户各阶段课程

#### Method URL

GET /api/weChat/user/queryPersonalCourse/\<int:status>/<openid>

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型 | 说明 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

#### Response

| 返回字段 | 字段类型   | 说明     |
| -------- | ---------- | -------- |
| msg      | String     | 请求结果 |
| code     | Int        | 请求状态 |
| data     | Dictionary | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### data 字典说明

| key   | value | 说明         |
| ----- | ----- | ------------ |
| items | 数组  | 存放所有数据 |

#### items 说明

| key         | value    |
| ----------- | -------- |
| cid         | 课程Id   |
| title       | 课程标题 |
| subject     | 补习科目 |
| grade       | 补习年级 |
| remark      | 备注     |
| courseTime  | 补习时间 |
| coursePlace | 补习地点 |
| userFee     | 课程价格 |
| createTime  | 创建时间 |



#### 调用示例

{

}

#### 返回示例

{

"msg" : "success",

"code" : 0,

"data" : {

​				"items":[{'cid':1, 'title':'哈哈'.......}]

​				}

}



### 【获取用户信息】 ###

#### Description ####

获取用户详细信息

#### Method URL

POST /api/weChat/user/getUser/<openid>

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型 | 说明 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

#### Response

| 返回字段 | 字段类型   | 说明     |
| -------- | ---------- | -------- |
| msg      | String     | 请求结果 |
| code     | Int        | 请求状态 |
| data     | Dictionary | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### data 字典说明

| key         | value  | 说明     |
| ----------- | ------ | -------- |
| name        | String | 姓名     |
| phoneNumber | String | 联系方式 |



#### 调用示例

{

}

#### 返回示例

{

"msg" : "success",

"code" : 0,

"data" : {

​				"name":"王恒",

​				"phoneNumber":"15343614950“

​				}

}



### 【预约教师】 ###

#### Description ####

预约教师，需要在url中传参

#### Method URL

POST /api/weChat/user/reserveTeacher/<openid>/<tid>

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型 | 说明 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

#### Response

| 返回字段 | 字段类型   | 说明     |
| -------- | ---------- | -------- |
| msg      | String     | 请求结果 |
| code     | Int        | 请求状态 |
| data     | Dictionary | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |



#### 调用示例

{

}

#### 返回示例

{

"msg" : "预约成功",

"code" : 0,

"data" : {}

}





## teacher

### 【检查是否已注册】 ###

#### Description ####

检查用户是否已注册

#### Method URL

POST /api/weChat/teacher/isRegistered

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型   | 说明               |
| ---- | ---- | ------ | ------------------ |
| code | true | String | 用来获取openid的？ |

#### Response

| 返回字段     | 字段类型 | 说明     |
| ------------ | -------- | -------- |
| isRegistered | Boolean  | 返回结果 |
| openid       | String   | openid   |

#### isRegistered 参数说明

| isRegistered 值 | 说明   |
| --------------- | ------ |
| True            | 已注册 |
| False           | 未注册 |



#### 调用示例

{

}

#### 返回示例

{

"isRegistered" : "False",

"openid" : "adsfasdfjalknmnzbnlakfw"

}



### 【注册】 ###

#### Description ####

教师注册（仅注册）

#### Method URL

POST /api/weChat/teacher/register

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数        | 必选 | 类型   | 说明                   |
| ----------- | ---- | ------ | ---------------------- |
| phoneNumber | true | String | 用于验证验证码是否正确 |

#### Response

| 返回字段 | 字段类型   | 说明     |
| -------- | ---------- | -------- |
| msg      | String     | 请求结果 |
| code     | Int        | 请求状态 |
| data     | Dictionary | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### 调用示例

{

}

#### 返回示例

{

"msg" : "注册成功",

"code" : 0,

"data" : {}

}



### 【查询可接订单】 ###

#### Description ####

教师查询可以投递订单（自动过滤自己已接订单）

#### Method URL

POST /api/weChat/teacher/getOrders/<openid>

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型 | 说明 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

#### Response

| 返回字段 | 字段类型   | 说明     |
| -------- | ---------- | -------- |
| msg      | String     | 请求结果 |
| code     | Int        | 请求状态 |
| data     | Dictionary | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### data 参数说明

| data值 | 说明                         |
| ------ | ---------------------------- |
| items  | 返回数据，是一个装字典的数组 |

#### items 数组值说明

| key         | value    |
| ----------- | -------- |
| cid         | 课程Id   |
| title       | 标题     |
| subject     | 课程     |
| grade       | 年级     |
| remark      | 备注     |
| courseTime  | 课程时间 |
| coursePlace | 课程地点 |
| teacherFee  | 课时薪酬 |
| hours       | 总课时   |
| createTime  | 创建时间 |



#### 调用示例

{

}

#### 返回示例

{

"msg" : "注册成功",

"code" : 0,

"data" : {

​				"items":[{'cid':1,'title':'高三语文'.......}]

​				}

}
