# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_131_PrepareExecuteSelectStatementParams(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_131)

  def run_test_131(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      stmt = DbtPy.prepare( conn, "SELECT id, breed, name, weight FROM animals WHERE id = ?" )
    
      if (DbtPy.execute(stmt, (0,))):
        row = DbtPy.fetch_tuple(stmt)
        while ( row ):
          #row.each { |child| print child }
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
