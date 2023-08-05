# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_113_DateTest(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_113)

  def run_test_113(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      drop = "DROP TABLE datetest"
      try:
        DbtPy.exec_immediate( conn, drop )
      except:
        pass
      
      create = "CREATE TABLE datetest ( id INTEGER, mydate DATE )"
      DbtPy.exec_immediate(conn, create)

      insert = "INSERT INTO datetest (id, mydate) VALUES (1,'03-27-1982')"
      DbtPy.exec_immediate(conn, insert)
      insert = "INSERT INTO datetest (id, mydate) VALUES (2,'07-08-1981')"
      DbtPy.exec_immediate(conn, insert)
      
      stmt = DbtPy.prepare(conn, "SELECT * FROM datetest")
      DbtPy.execute(stmt)

      result = DbtPy.fetch_row( stmt )
      while ( result ):
        row0 = DbtPy.result(stmt, 0)
        row1 = DbtPy.result(stmt, 1)
        print(row0)
        print(row1)
        result = DbtPy.fetch_row( stmt )
    else:
      print("Connection failed.")

#__END__
#__IDS_EXPECTED__
#1
#1982-03-27
#2
#1981-07-08
