# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_040_FetchTuple(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_040)
  
  def run_test_040(self): 
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)
      
    # Drop the test table, in case it exists
    drop = 'DROP TABLE animals'
    try:
      result = DbtPy.exec_immediate(conn, drop)
    except:
      pass
      
    # Create the test table
    create = 'CREATE TABLE animals (id INTEGER, breed VARCHAR(32), name CHAR(16), weight DECIMAL(7,2))'
    result = DbtPy.exec_immediate(conn, create)
      
    insert = "INSERT INTO animals values (0, 'cat', 'Pook', 3.2)"
      
    DbtPy.exec_immediate(conn, insert)
      
    stmt = DbtPy.exec_immediate(conn, "select * from animals")
    
    onerow = DbtPy.fetch_tuple(stmt)
     
    for element in onerow:
      print(element)

    DbtPy.rollback(conn)

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
