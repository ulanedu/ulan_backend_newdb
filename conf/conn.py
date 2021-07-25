from DBUtils.PooledDB import PooledDB
import pymysql

DbIp = 'youlanedu.com'
Dbuser = 'youlanedu_com'
Dbpass = '43NDcdxxWG'
database = 'test'

POOL = PooledDB(
    creator = pymysql,        # 使用链接数据库的模块
    maxconnections = 100,     # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached = 5,            # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
    maxcached = 10,           # 链接池中最多闲置的链接，0和None不限制
    blocking = True,          # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    maxusage = None,          # 一个链接最多被重复使用的次数，None表示无限制
    setsession = [],          # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    ping = 0,                 # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
    host = DbIp,
    port = 3306,
    user = Dbuser,
    password = Dbpass,
    database = database,
    charset = 'utf8'
)


class getCursor(object):
    def __init__(self):
        self.conn = POOL.connection()
        self.cs = self.conn.cursor()

    def __enter__(self):
        return self.cs

    def __exit__(self, exc_type, exc_val, exc_tb):
        if(exc_type != None):
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cs.close()


def connect_without_pool(database):
    db = pymysql.connect(DbIp, Dbuser, Dbpass, database)
    return db