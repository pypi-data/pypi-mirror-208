#

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_264_InsertRetrieveBIGINTTypeColumn(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_264)

  def run_test_264(self):
    # Make a connection
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    if conn:
       server = DbtPy.server_info( conn )
       if (server.DBMS_NAME[0:3] == 'Inf'):
          op = {DbtPy.ATTR_CASE: DbtPy.CASE_UPPER}
          DbtPy.set_option(conn, op, 1)

       # Drop the tab_bigint table, in case it exists
       drop = 'DROP TABLE tab_bigint'
       result = ''
       try:
         result = DbtPy.exec_immediate(conn, drop)
       except:
         pass
       # Create the tab_bigint table
       if (server.DBMS_NAME[0:3] == 'Inf'):
          create = "CREATE TABLE tab_bigint (col1 INT8, col2 INT8, col3 INT8, col4 INT8)"
       else:
          create = "CREATE TABLE tab_bigint (col1 BIGINT, col2 BIGINT, col3 BIGINT, col4 BIGINT)"
       result = DbtPy.exec_immediate(conn, create)

       insert = "INSERT INTO tab_bigint values (-9223372036854775807, 9223372036854775807, 0, NULL)"
       res = DbtPy.exec_immediate(conn, insert)
       print("Number of inserted rows:", DbtPy.num_rows(res))

       stmt = DbtPy.prepare(conn, "SELECT * FROM tab_bigint")
       DbtPy.execute(stmt)
       data = DbtPy.fetch_both(stmt)
       while ( data ):
         print(data[0])
         print(data[1])
         print(data[2])
         print(data[3])
         print(type(data[0]) is int)
         print(type(data[1]) is int) 
         print(type(data[2]) is int)
         data = DbtPy.fetch_both(stmt)

       # test DbtPy.result for fetch of bigint
       stmt1 = DbtPy.prepare(conn, "SELECT col2 FROM tab_bigint")
       DbtPy.execute(stmt1)
       DbtPy.fetch_row(stmt1, 0)
       if (server.DBMS_NAME[0:3] != 'Inf'):
         row1 = DbtPy.result(stmt1, 'COL2')
       else:
         row1 = DbtPy.result(stmt1, 'col2')
       print(row1)
       
       DbtPy.close(conn)

#__END__
#__LUW_EXPECTED__
#Number of inserted rows: 1
#-9223372036854775807
#9223372036854775807
#0
#None
#True
#True
#True
#9223372036854775807
#__ZOS_EXPECTED__
#Number of inserted rows: 1
#-9223372036854775807
#9223372036854775807
#0
#None
#True
#True
#True
#9223372036854775807
#__SYSTEMI_EXPECTED__
#Number of inserted rows: 1
#-9223372036854775807
#9223372036854775807
#0
#None
#True
#True
#True
#9223372036854775807
#__IDS_EXPECTED__
#Number of inserted rows: 1
#-9223372036854775807
#9223372036854775807
#0
#None
#True
#True
#True
#9223372036854775807
