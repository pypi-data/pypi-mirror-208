#

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_311_InsertSelectDeleteNumLiterals(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_311)

  def run_test_311(self):
    # Make a connection
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    if conn:
       DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_ON )

       # Drop the tab_num_literals table, in case it exists
       drop = 'DROP TABLE tab_num_literals'
       result = ''
       try:
         result = DbtPy.exec_immediate(conn, drop)
       except:
         pass
       # Create the animal table
       create = "CREATE TABLE tab_num_literals (col1 INTEGER, col2 FLOAT, col3 DECIMAL(7,2))"
       result = DbtPy.exec_immediate(conn, create)
   
       insert = "INSERT INTO tab_num_literals values ('11.22', '33.44', '55.66')"
       res = DbtPy.exec_immediate(conn, insert)
       print("Number of inserted rows:", DbtPy.num_rows(res))

       stmt = DbtPy.prepare(conn, "SELECT col1, col2, col3 FROM tab_num_literals WHERE col1 = '11'")
       DbtPy.execute(stmt)
       data = DbtPy.fetch_both(stmt)
       while ( data ):
         print(data[0])
         print(data[1])
         print(data[2])
         data = DbtPy.fetch_both(stmt)

       sql = "UPDATE tab_num_literals SET col1 = 77 WHERE col2 = 33.44"
       res = DbtPy.exec_immediate(conn, sql)
       print("Number of updated rows:", DbtPy.num_rows(res))

       stmt = DbtPy.prepare(conn, "SELECT col1, col2, col3 FROM tab_num_literals WHERE col2 > '33'")
       DbtPy.execute(stmt)
       data = DbtPy.fetch_both(stmt)
       while ( data ):
         print(data[0])
         print(data[1])
         print(data[2])
         data = DbtPy.fetch_both(stmt)
	 
       sql = "DELETE FROM tab_num_literals WHERE col1 > '10.0'"
       res = DbtPy.exec_immediate(conn, sql)
       print("Number of deleted rows:", DbtPy.num_rows(res))

       stmt = DbtPy.prepare(conn, "SELECT col1, col2, col3 FROM tab_num_literals WHERE col3 < '56'")
       DbtPy.execute(stmt)
       data = DbtPy.fetch_both(stmt)
       while ( data ):
         print(data[0])
         print(data[1])
         print(data[2])
         data = DbtPy.fetch_both(stmt)

       DbtPy.rollback(conn)
       DbtPy.close(conn)

#__END__
#__LUW_EXPECTED__
#Number of inserted rows: 1
#11
#33.44
#55.66
#Number of updated rows: 1
#77
#33.44
#55.66
#Number of deleted rows: 1
#__ZOS_EXPECTED__
#Number of inserted rows: 1
#11
#33.44
#55.66
#Number of updated rows: 1
#77
#33.44
#55.66
#Number of deleted rows: 1
#__SYSTEMI_EXPECTED__
#Number of inserted rows: 1
#11
#33.44
#55.66
#Number of updated rows: 1
#77
#33.44
#55.66
#Number of deleted rows: 1
#__IDS_EXPECTED__
#Number of inserted rows: 1
#11
#33.44
#55.66
#Number of updated rows: 1
#77
#33.44
#55.66
#Number of deleted rows: 1
