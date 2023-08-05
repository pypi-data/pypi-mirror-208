# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_145_BindRetrieveNoneEmptyString(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_145)

  def run_test_145(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    if conn:
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)

      stmt = DbtPy.prepare(conn, "INSERT INTO animals (id, breed, name) VALUES (?, ?, ?)")

      id = 999
      breed = None
      name = 'PythonDS'
      DbtPy.bind_param(stmt, 1, id)
      DbtPy.bind_param(stmt, 2, breed)
      DbtPy.bind_param(stmt, 3, name)

      # After this statement, we expect that the BREED column will contain
      # an SQL NULL value, while the NAME column contains an empty string

      DbtPy.execute(stmt)

      # After this statement, we expect that the BREED column will contain
      # an SQL NULL value, while the NAME column contains an empty string.
      # Use the dynamically bound parameters to ensure that the code paths
      # for both DbtPy.bind_param and DbtPy.execute treat Python Nones and empty
      # strings the right way.

      DbtPy.execute(stmt, (1000, None, 'PythonDS'))

      result = DbtPy.exec_immediate(conn, "SELECT id, breed, name FROM animals WHERE breed IS NULL")
      row = DbtPy.fetch_tuple(result)
      while ( row ): 
        for i in row:
          print(i)
        row = DbtPy.fetch_tuple(result)

      DbtPy.rollback(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#999
#None
#PythonDS        
#1000
#None
#PythonDS        
#__ZOS_EXPECTED__
#999
#None
#PythonDS        
#1000
#None
#PythonDS        
#__SYSTEMI_EXPECTED__
#999
#None
#PythonDS        
#1000
#None
#PythonDS        
#__IDS_EXPECTED__
#999
#None
#PythonDS        
#1000
#None
#PythonDS        
