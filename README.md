# 微信接口文档 #

URL:https://api.youlanedu.com/

## common ##

### 【获取验证码】 ###

#### Description ####

向用户手机发送验证码

#### Method URL

POST api/weChat/common/getCaptcha

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数        | 必选 | 类型   | 说明   |
| ----------- | ---- | ------ | ------ |
| phoneNumber | true | String | 手机号 |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

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

GET api/weChat/user/queryPersonalCourse/${status}/${openid}

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型 | 说明 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### data 字典说明

| key   | value      | 说明         |
| ----- | ---------- | ------------ |
| items | Json Array | 存放所有数据 |

#### items 数据项说明

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

获取用户详细信息（根据前端需求修改）

#### Method URL

POST api/weChat/user/getUser/${openid}

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型 | 说明 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

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

预约教师

#### Method URL

POST api/weChat/user/reserveTeacher/${openid}/${tid}

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

POST api/weChat/teacher/isRegistered

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数 | 必选 | 类型   | 说明                 |
| ---- | ---- | ------ | -------------------- |
| code | true | String | 用来获取openid的？？ |

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

POST api/weChat/teacher/register

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数        | 必选 | 类型   | 说明   |
| ----------- | ---- | ------ | ------ |
| phoneNumber | true | String | 手机号 |
| captcha     | true | String | 验证码 |

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

教师查询可以投递的课程（自动过滤自己已投递的课程）

#### Method URL

POST api/weChat/teacher/getOrders/${openid}

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型 | 说明 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### data 字典说明

| key   | value      | 说明         |
| ----- | ---------- | ------------ |
| items | Json Array | 返回查询数据 |

#### items 数据项说明

| key         | value                  |
| :---------- | :--------------------- |
| cid         | 课程Id                 |
| title       | 标题                   |
| subject     | 课程                   |
| grade       | 年级                   |
| remark      | 备注                   |
| courseTime  | 课程时间               |
| coursePlace | 课程地点               |
| teacherFee  | 课时薪酬（单小时薪酬） |
| hours       | 总课时                 |
| createTime  | 创建时间               |



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



### 【投递课程】 ###

#### Description ####

教师查询可以投递的课程（自动过滤自己已投递的课程）

#### Method URL

POST api/weChat/teacher/candidate

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数   | 必选 | 类型   | 说明         |
| ------ | ---- | ------ | ------------ |
| cid    | true | Int    | 投递课程Id   |
| openid | true | String | 投递人openid |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

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

"msg" : "投递成功!",

"code" : 0,

"data" : {}

}



### 【取消投递】 ###

#### Description ####

取消已经投递的课程

#### Method URL

POST api/weChat/teacher/cancel

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数   | 必选 | 类型   | 说明             |
| ------ | ---- | ------ | ---------------- |
| cid    | true | Int    | 取消投递课程的Id |
| openid | true | String | 投递人openid     |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

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

"msg" : "已取消投递",

"code" : 0,

"data" : {}

}

### 【获取投递订单】 ###

#### Description ####

教师查询可以投递的课程（自动过滤自己已投递的课程）

#### Method URL

POST api/weChat/teacher/getCandidatedOrders/${status}/${openid}

#### Headers

| 参数 | 值   |
| ---- | ---- |
|      |      |

#### Data

| 参数 | 必选 | 类型 | 说明 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### data 字典说明

| key   | value      | 说明         |
| ----- | ---------- | ------------ |
| items | Json Array | 返回查询数据 |

#### items 数据项说明

| key         | value                                                |
| :---------- | :--------------------------------------------------- |
| cid         | 课程Id                                               |
| tid         | 分配的教员Id                                         |
| title       | 标题                                                 |
| subject     | 补习课程                                             |
| grade       | 年级                                                 |
| remark      | 备注                                                 |
| courseTime  | 时间                                                 |
| coursePlace | 地点                                                 |
| teacherFee  | 课时薪酬                                             |
| hours       | 总课时                                               |
| status      | 课程进行状态（0分配教员，1试课中，2进行中，3已结课） |
| createTime  | 创建时间                                             |



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



### 【消课申请】 ###

#### Description ####

消课申请

#### Method URL

POST api/weChat/teacher/dismissalApplication

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数          | 必选 | 类型   | 说明         |
| ------------- | ---- | ------ | ------------ |
| cid           | true | Int    | 消课课程Id   |
| dismissedHour | true | String | 课程时长     |
| courseContent | true | String | 课程内容     |
| startTime     | true | String | 课程开始时间 |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

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

"msg" : "申请成功！",

"code" : 0,

"data" : {}

}



### 【课程讨论】 ###

#### Description ####

发布讨论

#### Method URL

POST api/weChat/teacher/courseDiscussion

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数    | 必选 | 类型   | 说明         |
| ------- | ---- | ------ | ------------ |
| cid     | true | Int    | 课程Id       |
| openid  | true | String | 讨论人openid |
| content | true | String | 讨论内容     |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

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

"msg" : "发布成功！",

"code" : 0,

"data" : {}

}



### 【获取教师简历】 ###

#### Description ####

获取教师简历

#### Method URL

POST api/weChat/teacher/getTeacherResume

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数   | 必选 | 类型   | 说明         |
| ------ | ---- | ------ | ------------ |
| openid | true | String | 讨论人openid |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

#### code 参数说明

| code 值 | 说明 |
| ------- | ---- |
| -1      | 失败 |
| 0       | 成功 |

#### data 参数说明

| key         | value  | 说明     |
| ----------- | ------ | -------- |
| tid         | Int    | 教师Id   |
| name        | String | 姓名     |
| sex         | String | 性别     |
| nation      | String | 民族     |
| politics    | String | 政治面貌 |
| email       | String | 邮箱号   |
| skilled     | String | 擅长科目 |
| hobbies     | String | 兴趣爱好 |
| school      | String | 学校     |
| major       | String | 专业     |
| grade       | String | 年级     |
| honour      | String | 所获荣誉 |
| teachExp    | String | 教学经历 |
| evaluation  | String | 个人评价 |
| freeTime    | String | 空闲时间 |
| avatarURL   | String | 头像url  |
| phoneNumber | String | 联系方式 |



#### 调用示例

{

}

#### 返回示例

{

"msg" : "发布成功！",

"code" : 0,

"data" : {

​			'tid':0,

​			'name':'王恒',

​			......

​			}

}

### 【修改简历】 ###

#### Description ####

修改简历

#### Method URL

POST api/weChat/teacher/updateResume

#### Headers

| 参数         | 值               |
| ------------ | ---------------- |
| content-type | application/json |

#### Data

| 参数   | 必选 | 类型   | 说明         |
| ------ | ---- | ------ | ------------ |
| form   | true | Json   | 修改数据字典 |
| openid | true | String | openid       |

#### form 参数说明

| key         | value  | 说明     |
| ----------- | ------ | -------- |
| name        | String | 姓名     |
| sex         | String | 性别     |
| nation      | String | 民族     |
| politics    | String | 政治面貌 |
| email       | String | 邮箱号   |
| skilled     | String | 擅长科目 |
| hobbies     | String | 兴趣爱好 |
| school      | String | 学校     |
| major       | String | 专业     |
| grade       | String | 年级     |
| honour      | String | 所获荣誉 |
| teachExp    | String | 教学经历 |
| evaluation  | String | 个人评价 |
| freeTime    | String | 空闲时间 |
| avatarURL   | String | 头像url  |
| phoneNumber | String | 联系方式 |

#### Response

| 返回字段 | 字段类型 | 说明     |
| -------- | -------- | -------- |
| msg      | String   | 请求结果 |
| code     | Int      | 请求状态 |
| data     | Json     | 请求数据 |

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

"msg" : "发布成功！",

"code" : 0,

"data" : {}

}
