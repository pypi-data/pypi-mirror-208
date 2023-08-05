# 

#

#

import unittest, sys
import DbtPy
import config
import os
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_122_FieldNameDiffCaseColNames(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_122)

  def run_test_122(self):
    os.environ['DELIMIDENT'] = 'y' 
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    if conn:
      drop = "drop table ftest"
      try:
        DbtPy.exec_immediate( conn, drop )
      except:
        pass
      
      create = "create table ftest ( \"TEST\" integer, \"test\" integer, \"Test\" integer  )"
      DbtPy.exec_immediate(conn, create)
      
      insert = "INSERT INTO ftest values (1,2,3)"
      DbtPy.exec_immediate(conn, insert)
      
      stmt = DbtPy.exec_immediate(conn, "SELECT * FROM ftest")
    
      num1 = DbtPy.field_name(stmt, 0)
      num2 = DbtPy.field_name(stmt, 1)
      num3 = DbtPy.field_name(stmt, 2)
      
      num4 = DbtPy.field_name(stmt, "TEST")
      num5 = DbtPy.field_name(stmt, 'test')
      num6 = DbtPy.field_name(stmt, 'Test')

      print("string(%d) \"%s\"" % (len(num1), num1))
      print("string(%d) \"%s\"" % (len(num2), num2))
      print("string(%d) \"%s\"" % (len(num3), num3))

      print("string(%d) \"%s\"" % (len(num4), num4))
      print("string(%d) \"%s\"" % (len(num5), num5))
      print("string(%d) \"%s\"" % (len(num6), num6))
      
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#string(4) "TEST"
#string(4) "test"
#string(4) "Test"
#string(4) "TEST"
#string(4) "test"
#string(4) "Test"
#__ZOS_EXPECTED__
#string(4) "TEST"
#string(4) "test"
#string(4) "Test"
#string(4) "TEST"
#string(4) "test"
#string(4) "Test"
#__SYSTEMI_EXPECTED__
#string(4) "TEST"
#string(4) "test"
#string(4) "Test"
#string(4) "TEST"
#string(4) "test"
#string(4) "Test"
#__IDS_EXPECTED__
#string(4) "TEST"
#string(4) "test"
#string(4) "Test"
#string(4) "TEST"
#string(4) "test"
#string(4) "Test"
