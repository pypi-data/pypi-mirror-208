

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class Wrapper(str):
  def __del__(self):
    print("Wrapper(" + self + ") being deleted")

class DbtPyTestCase(unittest.TestCase):

  def test_312_CacheBoundParameters(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_312)
  
  def run_test_312(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)
    
    query = "INSERT INTO department (deptno, deptname, mgrno, admrdept, location) VALUES (?, ?, ?, ?, ?)"
    
    if conn:
      stmt = DbtPy.prepare(conn, query)
      params = ['STG', 'Systems & Technology', '123456', 'RSF', 'Fiji']

      print("Binding parameters")
      for i,p in enumerate(params, 1):
        DbtPy.bind_param(stmt, i, Wrapper(p))
      
      if DbtPy.execute(stmt):
        print("Executing statement")
        DbtPy.execute(stmt)

        # force the cache to be unbound
        for i,p in enumerate(params, 1):
          DbtPy.bind_param(stmt, i, p)
        
        DbtPy.rollback(conn)
      else:
        print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#Binding parameters
#Executing statement
#Wrapper(STG) being deleted
#Wrapper(Systems & Technology) being deleted
#Wrapper(123456) being deleted
#Wrapper(RSF) being deleted
#Wrapper(Fiji) being deleted
#__ZOS_EXPECTED__
#Binding parameters
#Executing statement
#Wrapper(STG) being deleted
#Wrapper(Systems & Technology) being deleted
#Wrapper(123456) being deleted
#Wrapper(RSF) being deleted
#Wrapper(Fiji) being deleted
#__SYSTEMI_EXPECTED__
#Binding parameters
#Executing statement
#Wrapper(STG) being deleted
#Wrapper(Systems & Technology) being deleted
#Wrapper(123456) being deleted
#Wrapper(RSF) being deleted
#Wrapper(Fiji) being deleted
#__IDS_EXPECTED__
#Binding parameters
#Executing statement
#Wrapper(STG) being deleted
#Wrapper(Systems & Technology) being deleted
#Wrapper(123456) being deleted
#Wrapper(RSF) being deleted
#Wrapper(Fiji) being deleted
