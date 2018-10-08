#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

reload(sys)
sys.setdefaultencoding('utf-8')


class MySQLDB(object):
    def __init__(self, host='localhost', port=3306, user='root', password=None, charset="utf8mb4", db=None):
        self._connect_timeout = 5 # 5s
        self._connect_try_times = 3 #

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.charset = charset
        self.db = db
        self._pool = None

        self.reconnect()

    @property
    def dbcur(self):
        """获取游标
        """
        try:
            return self.cur
        except (MySQLdb.OperationalError, MySQLdb.InterfaceError):
            self.reconnect()
            return self.cur

    def reconnect(self):
        try_times = self._connect_try_times
        connect_status = False
        while not connect_status and try_times > 0:
            try_times -= 1
            try:
                self.reconnect_once()
                connect_status = True
            except Exception as e:
                print e
                print("Mysql error %d: %s" % (e.args[0], e.args[1]))
                time.sleep(2)

    @property
    def connection(self):
        if self._pool is None:
            self._pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=20,
                    host=self.host, port=self.port, user=self.user,
                    passwd=self.password, db=self.db, use_unicode=False,
                    charset=self.charset, cursorclass=DictCursor)

        return self._pool.connection()

    def reconnect_once(self):
        '''
        # self.close()
        # 连接设置
        self.conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.password, connect_timeout=self._connect_timeout)
        # 设置编码
        self.conn.set_character_set(self.charset)
        '''
        self.conn = self.connection
        # 获取游标
        self.conn.ping(True) # If it has gone down, an automatic reconnection is attempted.
        self.cur = self.conn.cursor()

        if self.db:
            self.select_db(self.db)

        '''
        # 2006: MySQL server has gone away
        self.conn.ping() # If it has gone down, an automatic reconnection is attempted.
        self.conn.database = self.db_name
        self.cur = self.conn.cursor()
        '''

    def select_db(self, db_name):
        '''Select database
        '''
        try:
            # self.conn.select_db(db_name)
            self.db_name = db_name
        except (MySQLdb.OperationalError, MySQLdb.InterfaceError):
            self.reconnect()
        except MySQLdb.Error, e:
            print "Mysql error %d: %s" % (e.args[0], e.args[1])

    def execute(self, sql, args=None):
        try:
            self.conn.ping()
        except:
            self.reconnect()
        finally:
            try:
                # 执行语句
                ret = self.dbcur.execute(sql, args)
                return ret
            except (MySQLdb.OperationalError, MySQLdb.InterfaceError):
                self.reconnect()
                ret = self.dbcur.execute(sql, args)
                return ret
            except MySQLdb.Error, e:
                print "Mysql error %d: %s" % (e.args[0], e.args[1])

    def executemany(self, sql, args=None):
        try:
            self.conn.ping()
        except:
            self.reconnect()
        finally:
            try:
                # 执行语句
                ret = self.dbcur.execute(sql, args)
                return ret
            except (MySQLdb.OperationalError, MySQLdb.InterfaceError):
                self.reconnect()
                ret = self.dbcur.executemany(sql, args)
                return ret
            except MySQLdb.Error, e:
                print "Mysql error %d: %s" % (e.args[0], e.args[1])

    def count(self, sql, args=None):
        self.execute(sql, args)
        ret = self.dbcur.fetchone()

        return ret[0]

    def query_one(self, sql, args=None):
        self.execute(sql, args)
        obj = self.dbcur.fetchone()

        if not obj:
            return obj

        desc = self.dbcur.description
        for k in obj:
            obj[k] = unicode(obj[k])
        return obj

    def query_all(self, sql, args=None):
        self.execute(sql, args)
        objs = self.dbcur.fetchall()
        desc = self.dbcur.description

        if not objs:
            return objs

        for obj in objs:
            for k in obj:
                obj[k] = unicode(obj[k])

        return objs

    def insert(self, table, data):
        keys = '`,`'.join(data.keys())
        values = data.values()
        placeholder = ','.join(['%s' for v in values])

        sql = 'replace INTO %(table)s (`%(keys)s`) VALUES (%(placeholder)s)'

        self.execute(sql % locals(), values)
        return self.dbcur.lastrowid

    def batch_insert(self, table, data):
        if not data or len(data) < 0:
            return
        keys = '`,`'.join(data[0].keys())

        sql = 'replace INTO %s (`%s`) VALUES (%s)' % (table, keys, ','.join(['%s' for _ in data[0]]))
        values = [[str(x[k]) for k in x] for x in data]

        ret = self.dbcur.executemany(sql, values)
        return ret

    # 提交事务，否则不能真正的插入数据
    def commit(self):
        try:
            self.conn.ping()
        except:
            self.reconnect()
        finally:
            try:
                self.conn.commit()
            except (MySQLdb.OperationalError, MySQLdb.InterfaceError):
                self.reconnect()
                self.conn.commit()

    # 关闭数据库连接，释放资源
    def close(self):
        if getattr(self, "dbcur", None) is not None:
            return
        self.dbcur.close()
        self.conn.close()
