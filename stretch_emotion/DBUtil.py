import mysql.connector

class DBUtil:
  def __init__(self):
    self.host = 'DB host name'
    self.database = 'DB name'
    self.user = 'user name'
    self.password = 'password'
    self.port = 'port (int)'
    self.connector = None
    self.cursor = None

  def createDBConnection(self):
    self.connector = mysql.connector.connect(
      user=self.user,
      password=self.password,
      port=self.port,
      host=self.host,
      database=self.database,
      auth_plugin='mysql_native_password'
    )
    self.cursor = self.connector.cursor()

  def closeDBConnection(self):
    self.cursor.close()
    self.connector.close()

  def executeQuery(self, sql):
    try:
      self.connector.autocommit = False
      self.cursor.execute(sql)
      self.connector.commit()
      return True

    except Exception as e:
      self.connector.roollback()
      print("SQL Execution ERROR!")
      print(str(e))
      return False

  def fetchAllQuery(self, sql):
    try:
      self.cursor.execute(sql)
      return self.cursor.fetchall()

    except Exception as e:
      print("Fetch Error!")
      print(str(e))
      self.closeDBConnection()
      return False

  def fetchSingleQuery(self, sql):
    try:
      self.cursor.execute(sql)
      result = self.cursor.fetchone()
      if not result: return []
      return result

    except Exception as e:
      print("Fetch Error!")
      print(str(e))
      return False
