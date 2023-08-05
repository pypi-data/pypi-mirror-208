# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):
  
  def test_010_UpdateRowCount(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_010)

  def run_test_010(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
     
    if conn:
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)
      stmt = DbtPy.exec_immediate(conn, "UPDATE animals SET name = 'flyweight' WHERE weight < 10.0")
      print("Number of affected rows: %d" % DbtPy.num_rows( stmt ))
      DbtPy.rollback(conn)
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#Number of affected rows: 4
#__ZOS_EXPECTED__
#Number of affected rows: 4
#__SYSTEMI_EXPECTED__
#Number of affected rows: 4
#__IDS_EXPECTED__
#Number of affected rows: 4
