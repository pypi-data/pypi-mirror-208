# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_114_NumericTest_01(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_114)

  def run_test_114(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      drop = "drop table numericliteral"

      try:
        DbtPy.exec_immediate( conn, drop )
      except:
        pass
      
      create = "create table numericliteral ( id INTEGER, num INTEGER )"
      DbtPy.exec_immediate(conn, create)
      
      insert = "INSERT INTO numericliteral (id, num) values (1,5)"
      DbtPy.exec_immediate(conn, insert)

      insert = "UPDATE numericliteral SET num = '10' WHERE num = '5'"
      DbtPy.exec_immediate(conn, insert)
      
      stmt = DbtPy.prepare(conn, "SELECT * FROM numericliteral")
      DbtPy.execute(stmt)

      result = DbtPy.fetch_row( stmt )
      while ( result ):
        row0 = DbtPy.result(stmt, 0)
        row1 = DbtPy.result(stmt, 1)
        print(row0)
        print(row1)
        result = DbtPy.fetch_row( stmt )
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#1
#10
#__ZOS_EXPECTED__
#1
#10
#__SYSTEMI_EXPECTED__
#1
#10
#__IDS_EXPECTED__
#1
#10
