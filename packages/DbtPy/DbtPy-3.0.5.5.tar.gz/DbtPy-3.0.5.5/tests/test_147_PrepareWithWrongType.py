# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_147_PrepareWithWrongType(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_147)

  def run_test_147(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)

      stmt = DbtPy.prepare(conn, "INSERT INTO animals (id, breed, name) VALUES (?, ?, ?)")
    
      id = "\"999\""
      breed = None
      name = 'PythonDS'
      try:
          DbtPy.bind_param(stmt, 1, id)
          DbtPy.bind_param(stmt, 2, breed)
          DbtPy.bind_param(stmt, 3, name)
       
          error = DbtPy.execute(stmt)
          print("Should not make it this far")
      except:
          excp = sys.exc_info()
          # slot 1 contains error message
          print(excp[1])
    else:
      print("Connection failed.")

#__END__
#__IDS_EXPECTED__
#Statement Execute Failed: [GBasedbt][GBase ODBC Driver]Invalid character value for cast specification. SQLCODE=-11106
