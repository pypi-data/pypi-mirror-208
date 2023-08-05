# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_003_NumAffectedRows(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_003)
    
  def run_test_003(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      
    if conn:
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)
      sql = 'UPDATE animals SET id = 9'
      res = DbtPy.exec_immediate(conn, sql)
      print("Number of affected rows: %d" % DbtPy.num_rows(res))
      DbtPy.rollback(conn)
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#Number of affected rows: 7
#__ZOS_EXPECTED__
#Number of affected rows: 7
#__SYSTEMI_EXPECTED__
#Number of affected rows: 7
#__IDS_EXPECTED__
#Number of affected rows: 7
