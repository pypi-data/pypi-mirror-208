# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_130_PrepExecuteSelectStmt(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_130)

  def run_test_130(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      stmt = DbtPy.prepare(conn, "SELECT id, breed, name, weight FROM animals WHERE id = 0")
    
      if DbtPy.execute(stmt):
        row = DbtPy.fetch_tuple(stmt)
        while ( row ):
          for i in row:
            print(i)
            row = DbtPy.fetch_tuple(stmt)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#0
#cat
#Pook            
#3.20
#__ZOS_EXPECTED__
#0
#cat
#Pook            
#3.20
#__SYSTEMI_EXPECTED__
#0
#cat
#Pook            
#3.20
#__IDS_EXPECTED__
#0
#cat
#Pook            
#3.20
