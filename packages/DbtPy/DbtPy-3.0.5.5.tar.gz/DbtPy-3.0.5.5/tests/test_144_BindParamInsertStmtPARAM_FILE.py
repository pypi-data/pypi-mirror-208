# 

#

#

import unittest, sys, os
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_144_BindParamInsertStmtPARAM_FILE(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_144)

  def run_test_144(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      # Drop the test table, in case it exists
      drop = 'DROP TABLE pictures'
      try:
        result = DbtPy.exec_immediate(conn, drop)
      except:
        pass
      
      # Create the test table
      create = 'CREATE TABLE pictures (id INTEGER, picture BLOB)'
      result = DbtPy.exec_immediate(conn, create)
      
      stmt = DbtPy.prepare(conn, "INSERT INTO pictures VALUES (0, ?)")
      
      picture = os.path.dirname(os.path.abspath(__file__)) + "/pic1.jpg"
      rc = DbtPy.bind_param(stmt, 1, picture, DbtPy.SQL_PARAM_INPUT)
    
      rc = DbtPy.execute(stmt)
      
      num = DbtPy.num_rows(stmt)
      
      print(num)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#1
#__ZOS_EXPECTED__
#1
#__SYSTEMI_EXPECTED__
#1
#__IDS_EXPECTED__
#1
