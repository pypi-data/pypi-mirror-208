# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_022_RollbackInsert(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_022)

  def run_test_022(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      
    if conn:
      stmt = DbtPy.exec_immediate(conn, "SELECT count(*) FROM animals")
      res = DbtPy.fetch_tuple(stmt)
      rows = res[0]
      print(rows)
        
      DbtPy.autocommit(conn, 0)
      ac = DbtPy.autocommit(conn)
      if ac != 0:
        print("Cannot set DbtPy.AUTOCOMMIT_OFF\nCannot run test")
        #continue
        
      DbtPy.exec_immediate(conn, "INSERT INTO animals values (7,'bug','Brain Bug',10000.1)")
        
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
#8
#7
#__ZOS_EXPECTED__
#7
#8
#7
#__SYSTEMI_EXPECTED__
#7
#8
#7
#__IDS_EXPECTED__
#7
#8
#7
