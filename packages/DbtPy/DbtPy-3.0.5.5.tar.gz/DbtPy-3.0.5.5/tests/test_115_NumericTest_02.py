# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_115_NumericTest_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_115)

  def run_test_115(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    server = DbtPy.server_info( conn )
    if (server.DBMS_NAME[0:3] == 'Inf'):
      op = {DbtPy.ATTR_CASE: DbtPy.CASE_UPPER}
      DbtPy.set_option(conn, op, 1)
    
    if conn:
      drop = "drop table numericliteral"
      try:
        DbtPy.exec_immediate( conn, drop )
      except:
        pass

      create = "create table numericliteral ( id INTEGER, data VARCHAR(50) )"
      DbtPy.exec_immediate(conn, create)

      insert = "INSERT INTO numericliteral (id, data) values (12, 'NUMERIC LITERAL TEST')"
      DbtPy.exec_immediate(conn, insert)

      stmt = DbtPy.prepare(conn, "SELECT data FROM numericliteral")
      DbtPy.execute(stmt)
      
#      NOTE: This is a workaround
#      function fetch_object() to be implemented...
#      row = DbtPy.fetch_object(stmt, 0)
      
      class Row:
          pass
      
      row = Row()
      DbtPy.fetch_row(stmt, 0)
      if (server.DBMS_NAME[0:3] != 'Inf'):
        row.DATA = DbtPy.result(stmt, 'DATA')
      else:
        row.DATA = DbtPy.result(stmt, 'data')
      print(row.DATA)

      insert = "UPDATE numericliteral SET data = '@@@@@@@@@@' WHERE id = '12'"
      DbtPy.exec_immediate(conn, insert)

      stmt = DbtPy.prepare(conn, "SELECT data FROM numericliteral")
      DbtPy.execute(stmt)
      
#      row = DbtPy.fetch_object(stmt, 0)
      DbtPy.fetch_row(stmt, 0)
      if (server.DBMS_NAME[0:3] != 'Inf'):
        row.DATA = DbtPy.result(stmt, 'DATA')
      else:
        row.DATA = DbtPy.result(stmt, 'data')
      print(row.DATA)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#NUMERIC LITERAL TEST
#@@@@@@@@@@
#__ZOS_EXPECTED__
#NUMERIC LITERAL TEST
#@@@@@@@@@@
#__SYSTEMI_EXPECTED__
#NUMERIC LITERAL TEST
#@@@@@@@@@@
#__IDS_EXPECTED__
#NUMERIC LITERAL TEST
#@@@@@@@@@@
