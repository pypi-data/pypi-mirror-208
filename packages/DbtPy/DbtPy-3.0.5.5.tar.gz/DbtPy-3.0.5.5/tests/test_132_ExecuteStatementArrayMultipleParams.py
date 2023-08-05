# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_132_ExecuteStatementArrayMultipleParams(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_132)

  def run_test_132(self):
    sql =  "SELECT id, breed, name, weight FROM animals WHERE id = ? AND name = ?"
    
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      stmt = DbtPy.prepare(conn, sql)
    
      if (DbtPy.execute(stmt, (0, 'Pook'))):
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
