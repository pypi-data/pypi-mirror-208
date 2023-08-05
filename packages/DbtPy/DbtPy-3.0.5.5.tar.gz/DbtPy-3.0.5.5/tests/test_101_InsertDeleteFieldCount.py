# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_101_InsertDeleteFieldCount(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_101)

  def run_test_101(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    if conn:
      result = DbtPy.exec_immediate(conn,"insert into t_string values(123,1.222333,'one to one')")
      if result:
        cols = DbtPy.num_fields(result)
        print("col: %d" % cols)
        rows = DbtPy.num_rows(result)
        print("affected row: %d" % rows)
      result = DbtPy.exec_immediate(conn,"delete from t_string where a=123")
      if result:
        cols = DbtPy.num_fields(result)
        print("col: %d" % cols)
        rows = DbtPy.num_rows(result)
        print("affected row: %d" % rows)
    else:
      print("no connection");    

#__END__
#__LUW_EXPECTED__
#col: 0
#affected row: 1
#col: 0
#affected row: 1
#__ZOS_EXPECTED__
#col: 0
#affected row: 1
#col: 0
#affected row: 1
#__SYSTEMI_EXPECTED__
#col: 0
#affected row: 1
#col: 0
#affected row: 1
#__IDS_EXPECTED__
#col: 0
#affected row: 1
#col: 0
#affected row: 1
