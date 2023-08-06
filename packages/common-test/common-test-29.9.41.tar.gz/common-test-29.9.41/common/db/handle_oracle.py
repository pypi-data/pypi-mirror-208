import sysconfig
import os
import cx_Oracle


# 封装的类
class Oracle(object):
  """  oracle db operator  """

  def __init__(self, userName, password, host, instance):
    self._conn = cx_Oracle.connect("%s/%s@%s/%s" % (userName, password, host, instance))
    self.cursor = self._conn.cursor()

  def queryTitle(self, sql, nameParams=None):
    if nameParams is None:
      nameParams = {}
    if len(nameParams) > 0:
      self.cursor.execute(sql, nameParams)
    else:
      self.cursor.execute(sql)

    colNames = []
    for i in range(0, len(self.cursor.description)):
      colNames.append(self.cursor.description[i][0])

    return colNames

  # query methods
  def queryAll(self, sql):
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def queryOne(self, sql):
    self.cursor.execute(sql)
    return self.cursor.fetchone()

  def queryBy(self, sql, nameParams=None):
    if nameParams is None:
      nameParams = {}
    if len(nameParams) > 0:
      self.cursor.execute(sql, nameParams)
    else:
      self.cursor.execute(sql)

    return self.cursor.fetchall()

  def insertBatch(self, sql, nameParams=None):
    """batch insert much rows one time,use location parameter"""
    if nameParams is None:
      nameParams = []
    self.cursor.prepare(sql)
    self.cursor.executemany(None, nameParams)
    self.commit()

  def commit(self):
    self._conn.commit()

  def __del__(self):
    if hasattr(self, 'cursor'):
      self.cursor.close()

    if hasattr(self, '_conn'):
      self._conn.close()


