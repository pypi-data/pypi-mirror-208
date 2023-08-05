# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_6561_InsertNULLValues(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_6561)

  def run_test_6561(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)

      stmt = DbtPy.exec_immediate(conn, "INSERT INTO animals (id, breed, name, weight) VALUES (null, null, null, null)")
      statement = "SELECT count(id) FROM animals"
      result = DbtPy.exec_immediate(conn, statement)
      if ( (not result) and DbtPy.stmt_error() ):
        print("ERROR: %s" % (DbtPy.stmt_errormsg(), ))

      row = DbtPy.fetch_tuple(result)
      while ( row ):
        for i in row:
            print(i)
        row = DbtPy.fetch_tuple(result)
    
      DbtPy.rollback(conn)
      DbtPy.close(conn)
      
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#7
#__ZOS_EXPECTED__
#7
#__SYSTEMI_EXPECTED__
#7
#__IDS_EXPECTED__
#7
