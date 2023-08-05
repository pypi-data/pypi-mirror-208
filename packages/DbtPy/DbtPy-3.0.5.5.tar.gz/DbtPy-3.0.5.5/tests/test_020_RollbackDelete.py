# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_020_RollbackDelete(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_020)

  def run_test_020(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      
    if conn:
        
      stmt = DbtPy.exec_immediate(conn, "SELECT count(*) FROM animals")
      res = DbtPy.fetch_tuple(stmt)
      rows = res[0]
      print(rows)
      
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)
      ac = DbtPy.autocommit(conn)
      if ac != 0:
        print("Cannot set DbtPy.SQL_AUTOCOMMIT_OFF\nCannot run test")
        #continue 
      
      DbtPy.exec_immediate(conn, "DELETE FROM animals")
      
      stmt = DbtPy.exec_immediate(conn, "SELECT count(*) FROM animals")
      res = DbtPy.fetch_tuple(stmt)
      rows = res[0]
      print(rows)
       
      DbtPy.rollback(conn)
       
      stmt = DbtPy.exec_immediate(conn, "SELECT count(*) FROM animals")
      res = DbtPy.fetch_tuple(stmt)
      rows = res[0]
      print(rows)
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#7
#0
#7
#__ZOS_EXPECTED__
#7
#0
#7
#__SYSTEMI_EXPECTED__
#7
#0
#7
#__IDS_EXPECTED__
#7
#0
#7
