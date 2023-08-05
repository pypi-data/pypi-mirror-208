# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_100_SelectDeleteInsertFieldCount(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_100)

  def run_test_100(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)

      stmt = DbtPy.exec_immediate(conn, "SELECT * FROM animals ORDER BY breed")
    
      fields1 = DbtPy.num_fields(stmt)
      
      print("int(%d)" % fields1)
      
      stmt = DbtPy.exec_immediate(conn, "SELECT name, breed FROM animals ORDER BY breed")
      fields2 = DbtPy.num_fields(stmt)
      
      print("int(%d)" % fields2)
      
      stmt = DbtPy.exec_immediate(conn, "DELETE FROM animals")
      fields3 = DbtPy.num_fields(stmt)
      
      print("int(%d)" % fields3)
      
      stmt = DbtPy.exec_immediate(conn, "INSERT INTO animals values (0, 'cat', 'Pook', 3.2)")
      fields4 = DbtPy.num_fields(stmt)
        
      print("int(%d)" % fields4)
      
      stmt = DbtPy.exec_immediate(conn, "SELECT name, breed, 'TEST' FROM animals")
      fields5 = DbtPy.num_fields(stmt)
        
      print("int(%d)" % fields5)

      DbtPy.rollback(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#int(4)
#int(2)
#int(0)
#int(0)
#int(3)
#__ZOS_EXPECTED__
#int(4)
#int(2)
#int(0)
#int(0)
#int(3)
#__SYSTEMI_EXPECTED__
#int(4)
#int(2)
#int(0)
#int(0)
#int(3)
#__IDS_EXPECTED__
#int(4)
#int(2)
#int(0)
#int(0)
#int(3)
