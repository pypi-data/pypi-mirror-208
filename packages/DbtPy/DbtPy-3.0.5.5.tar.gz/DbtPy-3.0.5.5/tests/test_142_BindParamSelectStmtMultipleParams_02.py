# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_142_BindParamSelectStmtMultipleParams_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_142)

  def run_test_142(self):
    sql = "SELECT id, breed, name, weight FROM animals WHERE weight < ? AND weight > ?"
    
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      stmt = DbtPy.prepare(conn, sql)
    
      weight = 200.05
      mass = 2.0
      
      DbtPy.bind_param(stmt, 1, weight, DbtPy.SQL_PARAM_INPUT)
      DbtPy.bind_param(stmt, 2, mass, DbtPy.SQL_PARAM_INPUT)
    
      result = DbtPy.execute(stmt) 
      if ( result ):
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
#5
#goat
#Rickety Ride    
#9.70
#6
#llama
#Sweater         
#150.00
#__ZOS_EXPECTED__
#0
#cat
#Pook            
#3.20
#1
#dog
#Peaches         
#12.30
#5
#goat
#Rickety Ride    
#9.70
#6
#llama
#Sweater         
#150.00
#__SYSTEMI_EXPECTED__
#0
#cat
#Pook            
#3.20
#1
#dog
#Peaches         
#12.30
#5
#goat
#Rickety Ride    
#9.70
#6
#llama
#Sweater         
#150.00
#__IDS_EXPECTED__
#0
#cat
#Pook            
#3.20
#1
#dog
#Peaches         
#12.30
#5
#goat
#Rickety Ride    
#9.70
#6
#llama
#Sweater         
#150.00
