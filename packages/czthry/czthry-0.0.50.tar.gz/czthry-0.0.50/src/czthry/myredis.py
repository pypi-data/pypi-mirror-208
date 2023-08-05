from redis import ConnectionPool, Redis
import time, json


DefaultHost = '127.0.0.1'
DefaultPort = 6379
DefaultDB = 0
RetryInterval = 5


class MyRedis(object):
    '''
    redis工具类，
    - 自动重连
    - 给key添加前缀，以区分其他数据
    - 基本的存取方法
    '''
    def __init__(self, prefix, host=None, port=None, db=None, password=None):
        self._redis = None
        if not prefix.endswith('_'):
            prefix += '_'
        self._prefix = prefix
        self._host = host if host else DefaultHost
        self._port = port if port else DefaultPort
        self._db   = db if db else DefaultDB
        self._password = password

    def close(self):
        if self._redis:
            try:
                self._redis.close()
            finally:
                self._redis = None

    def get(self, key):
        return self.redis.get(self.rkey(key))

    def set(self, key, data):
        self.redis.set(self.rkey(key), data)

    def getobj(self ,key, default=None):
        data = self.get(key)
        try:
            return json.loads(data)
        except:
            return default

    def setobj(self, key, obj):
        ''' 最直接的存储方法，obj序列化json字符串 '''
        data = json.dumps(obj)
        self.set(key, data)

    def hash_set(self, key, field, value):
        self.redis.hset(self.rkey(key), field, value)

    def hash_get(self, key, field):
        return self.redis.hget(self.rkey(key), field)

    def hash_del(self, key, fields):
        self.redis.hdel(self.rkey(key), fields)

    def list_set(self, key, arr):
        '''添加的数组元素，必须是基本类型'''
        for it in arr:
            self.redis.rpush(self.rkey(key), it)

    def list_get(self, key, default=[]):
        try:
            return self.redis.lrange(self.rkey(key), 0, -1)
        except:
            return default

    def list_clean(self, key):
        ''' 清空数组 '''
        self.redis.ltrim(self.rkey(key), -1, 0)

    def rkey(self, key):
        if key.startswith(self._prefix):
            return key
        return self._prefix + key

    @property
    def redis(self):
        try:
            self._redis.ping()
        except Exception as e:
            # None 或者 断开，需要重连
            while True:
                try:
                    pool = ConnectionPool(host=self._host, port=self._port, db=self._db, password=self._password, decode_responses=True, health_check_interval=30)
                    redis = Redis(connection_pool=pool)
                    redis.ping()
                except Exception as e:
                    print('redis连接失败,正在尝试重连(%s)' % e)
                    time.sleep(RetryInterval)
                    continue
                else:
                    self._redis = redis
                    break
        return self._redis
