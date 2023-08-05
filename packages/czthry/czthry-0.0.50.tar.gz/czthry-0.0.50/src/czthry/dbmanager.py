from sqlalchemy import create_engine
from sqlalchemy import text
from urllib.parse import quote_plus as urlquote
import re


# 数据已存在时的操作
ea_ignore = 'ignore'
ea_replace = 'replace'
ea_update = 'update'


def fill_empty_fields(keys, data):
    '''
    对于批量数据，
        data = [
            {'a':1,  'b':2, 'c': 3},
            {'a':11, 'b':22},
            ...
        ]
    依据给定keys
        keys = ['a', 'b', 'c']
    某些数据可能缺少字段，批量插入时
    因字段缺失报错，所以需要对缺少的数据填充，把源数据对齐

    注意不是对照table的fields来填充
    因为field缺失的话会按照数据表的定义自行处理

    注意多余的key不影响，keys是数据表"需要的，且能够提供的"字段，
    实际用到的key是由格式化sql来决定
    '''
    if type(data) == dict:
        arr = [data]
    else:
        arr = data
    for item in arr:
        for k in keys:
            if k not in item:
                item[k] = ''  # 填充空字符串即可


class DBManager(object):
    def __init__(self, connstr, **kwargs):
        self.engine = create_engine(connstr, echo=False, encoding='utf8', **kwargs)

    def insert(self, table, data, exist_action=ea_ignore):
        """
        :param table: 表名
        :param data: 数据
            dict 类型 是一条数据，key就是字段名，所以 key 很重要
            list 类型 是N条数据，是dict类型的数组，最终会转换成元组，批量执行
        :param exist_action:
            如果此条数据已存在，采取何种方式去插入：
                ignore: 'insert ignore into ...' 此次插入不执行
                replace: 'replace into ...' 替换现有记录（先delete 后insert。id会自增，不同于update）
                其他: 'insert into...' 直接插入。如果没有唯一索引，就会重复插入
        :return:

        """
        if not data:
            return None
        if type(data) == list:
            keys = list(data[0].keys())
        else:
            keys = list(data.keys())
        fields = ','.join(keys)  # 使用data的keys作为字段名
        pre_values = ','.join([':%s' % k for k in keys])  # 前缀加":"
        if exist_action == ea_replace:
            pre_sql = 'replace into %s (%s) values(%s)' % (table, fields, pre_values)
        elif exist_action == ea_ignore:
            pre_sql = 'insert ignore into %s (%s) values(%s)' % (table, fields, pre_values)
        elif exist_action == ea_update:
            updates = ','.join([f'{key}=values({key})' for key in keys])
            pre_sql = 'insert into %s (%s) values(%s)  on duplicate key update %s' % (table, fields, pre_values, updates)
        else:
            pre_sql = 'insert into %s (%s) values(%s)' % (table, fields, pre_values)
        session = None
        bind_sql = None
        try:
            bind_sql = text(pre_sql)
            session = self.engine.connect()
            if type(data) == list:
                resproxy = session.execute(bind_sql, *data)  # 对于数组，批量执行，效率非常高
            else:
                resproxy = session.execute(bind_sql, data)
            return resproxy
        except Exception as e:
            if bind_sql is not None:
                self.engine.logger.error('插入insert操作\n%s\n发生错误\n%s' % (bind_sql, e))
            return None
        finally:
            if session:
                session.close()

    def update(self, table, data):
        '''
        如果按唯一索引，有重复项，则更新data内的数据，其他不变
        如果没有，则插入
        '''
        return self.insert(table, data, exist_action=ea_update)

    def execute(self, sql):
        session = None
        try:
            session = self.engine.connect()
            result = session.execute(sql)
            find = re.search(r'^select', sql.lower().strip())
            if find:
                rows = result.fetchall()
                return rows
        except Exception as e:
            self.engine.logger.error('执行sql语句（%s）发生错误：%s' % (sql, e))
            return None
        finally:
            if session:
                session.close()

    def query(self, sql):
        result = self.execute(sql)
        if not result:
            return []
        result = [dict(row) for row in result]
        return result
        
    def exists(self, table, fields, data):
        condition = ''
        if fields:
            fmt = ' and '.join([f'{f}="%({f})s"' for f in fields])
            condition = 'where ' + fmt % data
        sql = f'select * from {table} {condition} limit 1'
        try:
            result = self.execute(sql)
            count = len(result)
            return count > 0
        except Exception as e:
            self.engine.logger.error('查询exists发生错误：%s' % e)
            return None

    def close(self):
        self.engine.dispose()

    def align_keys_by_table(self, table, data):
        '''
        依照数据表的定义来对齐字段。
        多余的字段丢掉
        '''
        if type(data) == dict:
            data = [data]
        data_keys = list(data[0].keys())
        database = self.engine.url.database
        sql = f'select COLUMN_NAME from information_schema.COLUMNS where TABLE_SCHEMA="{database}" and TABLE_NAME="{table}"'
        table_keys = self.execute(sql)
        if table_keys:
            table_keys = [r[0] for r in table_keys]
        for data_key in data_keys:
            if data_key not in table_keys:
                for it in data:
                    try:
                        # 值是None 也要删。但如果没有key，就会except
                        del it[data_key]
                    except:
                        # 要删除的key不存在。
                        pass
        return table_keys

    def align_data_keys(self, data, table):
        if not data:
            return False
        table_keys = self.align_keys_by_table(table, data)
        fill_empty_fields(table_keys, data)
        return True


if __name__ == '__main__':
    pass
