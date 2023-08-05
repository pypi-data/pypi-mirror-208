import redis
import sys
import traceback
import time
import numpy as np
import cv2
from loguru import logger

class RedisClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Singleton pattern
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, host, port, password=None):
        self.host = host
        self.port = port
        self.redis_conn = None
        try:
            self.pool = redis.ConnectionPool(host=self.host,
                                             port=self.port,
                                             decode_responses=True,
                                             db=0,
                                             password=password,
                                             max_connections=100)
            logger.info(f'获取Redis连接池, Host={self.host}, Port={self.port}')
        except Exception as e:
            logger.error("获取Redis连接池异常, 程序退出:{}Tracelog={}".format(str(e), traceback.format_exc()))
            sys.exit(0)

    def get_redis_client(self):
        try:
            if self.redis_conn is None or not self.redis_conn.ping():
                self.redis_conn = redis.StrictRedis(connection_pool=self.pool)

                if self.redis_conn.ping():
                    logger.success(f'获取Redis连接成功, Host={self.host}, Port={self.port}')
                self.redis_conn.flushall()
        except Exception as e:
            logger.error("Redis连接*异常*:{}, Tracelog={}".format(str(e), traceback.format_exc()))

    def get_redis_data(self, key):
        self.get_redis_client()
        try:
            res = self.redis_conn.get(key)
            redis_out = {'Frame': None, 'bFlag': False, 'error': False, 'iTargetNum': 0, 'iType': '', 'sType': ''}
            if res is not None:
                redis_data = eval(res)
                nparr = np.frombuffer(redis_data['Frame'], np.uint8)
                redis_out['Frame'] = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                result = redis_data.get('Result', {})
                i_type_list = [str(alg_type) for alg_type in result.keys()]
                s_type_list = [result[alg_type].get('sType', '') for alg_type in result.keys()]
                redis_out['iType'] = ','.join(i_type_list)
                redis_out['sType'] = ','.join(s_type_list)

                for algtype in result:
                    res_data = result[algtype]
                    redis_out['bFlag'] = redis_out['bFlag'] or res_data['bFlag']
                    redis_out['error'] = redis_out['error'] or res_data['error']
                    res_results = res_data.get('lResults', {})
                    rect = res_results.get('rect', [])
                    redis_out['iTargetNum'] += len(rect)
                    s_value = res_results.get('sValue', '')
                    if s_value:
                        redis_out['iTargetNum'] = s_value
            return redis_out
        except redis.exceptions.ConnectionError:
            logger.error("Redis连接已断开，重新连接中...")
            self.get_redis_client()
            return self.get_redis_data(key)
        except Exception as e:
            logger.error("获取Redis数据异常:{}, Tracelog={}".format(str(e), traceback.format_exc()))
            return None

    def gen_redis_data(self, key):
        while True:
            result = self.get_redis_data(key)
            if result is not None:
                yield result
            else:
                time.sleep(0.1)

if __name__ == '__main__':
    redis_client = RedisClient('10.10.8.43', 7777, '123456')
    gen_data = redis_client.gen_redis_data('cam_rtsp_left')

    for data in gen_data:
        if data.get('Frame', None) is not None:
            print(data['Frame'].shape)
        else:
            print('Frame data is None')
            time.sleep(0.1)
