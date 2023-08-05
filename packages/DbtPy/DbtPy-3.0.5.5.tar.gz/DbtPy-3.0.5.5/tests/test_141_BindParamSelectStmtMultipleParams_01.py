# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_141_BindParamSelectStmtMultipleParams_01(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_141)

  def run_test_141(self):
    sql = "SELECT id, breed, name, weight FROM animals WHERE id < ? AND weight > ?"
    
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      stmt = DbtPy.prepare(conn, sql)
    
      animal = 5
      mass = 2.0
      DbtPy.bind_param(stmt, 1, animal)
      DbtPy.bind_param(stmt, 2, mass)
    
      if DbtPy.execute(stmt):
        row = DbtPy.fetch_tuple(stmt)
        while ( row ): 
          #row.each { |child| print child }
          for i in row:
            print(i)
          row = DbtPy.fetch_tuple(stmt)
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#0
#cat
#Pook            
#3.20
#1
#dog
#Peaches         
#12.30
#2
#horse
#Smarty          
#350.00
#__ZOS_EXPECTED__
#0
#cat
#Pook            
#3.20
#1
#dog
#Peaches         
#12.30
#2
#horse
#Smarty          
#350.00
#__SYSTEMI_EXPECTED__
#0
#cat
#Pook            
#3.20
#1
#dog
#Peaches         
#12.30
#2
#horse
#Smarty          
#350.00
#__IDS_EXPECTED__
#0
#cat
#Pook            
#3.20
#1
#dog
#Peaches         
#12.30
#2
#horse
#Smarty          
#350.00
