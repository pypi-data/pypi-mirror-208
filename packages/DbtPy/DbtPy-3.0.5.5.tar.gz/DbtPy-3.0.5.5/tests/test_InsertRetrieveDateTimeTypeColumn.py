
import unittest, sys, datetime
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_InsertRetrieveDateTimeTypeColumn(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_InsertRetrieveDateTimeTypeColumn)

  def run_test_InsertRetrieveDateTimeTypeColumn(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      drop = 'DROP TABLE tab_datetime'
      result = ''
      try:
        result = DbtPy.exec_immediate(conn, drop)
      except:
        pass
      t_val = datetime.time(10, 42, 34)
      d_val = datetime.date(1981, 7, 8)
      #ts_val = datetime.datetime.today()
      ts_val = datetime.datetime(1981, 7, 8, 10, 42, 34, 10)
      server = DbtPy.server_info( conn )
      if (server.DBMS_NAME[0:3] == 'Inf'):
        statement = "CREATE TABLE tab_datetime (col1 DATETIME HOUR TO SECOND, col2 DATE, col3 DATETIME YEAR TO FRACTION(5))"
        result = DbtPy.exec_immediate(conn, statement)
        statement = "INSERT INTO tab_datetime (col1, col2, col3) values (?, ?, ?)"
        stmt = DbtPy.prepare(conn, statement)
        result = DbtPy.execute(stmt, (t_val, d_val, ts_val))
      else:
        statement = "CREATE TABLE tab_datetime (col1 TIME, col2 DATE, col3 TIMESTAMP)"
        result = DbtPy.exec_immediate(conn, statement)
        statement = "INSERT INTO tab_datetime (col1, col2, col3) values (?, ?, ?)"
        stmt = DbtPy.prepare(conn, statement)
        result = DbtPy.execute(stmt, (t_val, d_val, ts_val))

      statement = "SELECT * FROM tab_datetime"
      result = DbtPy.exec_immediate(conn, statement)
      
      for i in range(0, DbtPy.num_fields(result)):
        print(str(i) + ":" + DbtPy.field_type(result,i))

      statement = "SELECT * FROM tab_datetime"
      stmt = DbtPy.prepare(conn, statement)
      rc = DbtPy.execute(stmt)
      result = DbtPy.fetch_row(stmt)
      while ( result ):
        row0 = DbtPy.result(stmt, 0)
        row1 = DbtPy.result(stmt, 1)
        row2 = DbtPy.result(stmt, 2)
        print(type(row0), row0)
        print(type(row1), row1)
        print(type(row2), row2)
        result = DbtPy.fetch_row(stmt)
      
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#0:time
#1:date
#2:timestamp
#<%s 'datetime.time'> 10:42:34
#<%s 'datetime.date'> 1981-07-08
#<%s 'datetime.datetime'> 1981-07-08 10:42:34.000010
#__ZOS_EXPECTED__
#0:time
#1:date
#2:timestamp
#<%s 'datetime.time'> 10:42:34
#<%s 'datetime.date'> 1981-07-08
#<%s 'datetime.datetime'> 1981-07-08 10:42:34.000010
#__SYSTEMI_EXPECTED__
#0:time
#1:date
#2:timestamp
#<%s 'datetime.time'> 10:42:34
#<%s 'datetime.date'> 1981-07-08
#<%s 'datetime.datetime'> 1981-07-08 10:42:34.000010
#__IDS_EXPECTED__
#0:time
#1:date
#2:timestamp
#<%s 'datetime.time'> 10:42:34
#<%s 'datetime.date'> 1981-07-08
#<%s 'datetime.datetime'> 1981-07-08 10:42:34.000010
