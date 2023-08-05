#

#

#

import unittest, sys, os
import DbtPy
#need to add this line below to each file to make the connect parameters available to all the test files
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_314_Collection_Param(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_314)

  def run_test_314(self):
    # Make a connection
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    # Get the server type
    server = DbtPy.server_info( conn )

    try:
        sql = "drop table coll_param_tab;"
        stmt = DbtPy.exec_immediate(conn, sql)
    except:
        pass

    sql = "create table coll_param_tab (c1 int, c2 SET(VARCHAR(100)NOT NULL), c3 MULTISET(int not null), c4 LIST(int not null), c5 ROW(name varchar(15), addr varchar(15), zip varchar(15) ) );"
    stmt = DbtPy.exec_immediate(conn, sql)

    sql = "INSERT INTO coll_param_tab VALUES (?, ?, ?, ?, ?);"
    stmt = DbtPy.prepare(conn, sql)

    c1 = None
    c2 = None
    c3 = None
    c4 = None    
    c5 = None

    DbtPy.bind_param(stmt, 1, c1, DbtPy.SQL_PARAM_INPUT, DbtPy.SQL_INTEGER)
    DbtPy.bind_param(stmt, 2, c2, DbtPy.SQL_PARAM_INPUT, DbtPy.SQL_VARCHAR,  DbtPy.SQL_INFX_RC_COLLECTION)
    DbtPy.bind_param(stmt, 3, c3, DbtPy.SQL_PARAM_INPUT, DbtPy.SQL_CHAR, DbtPy.SQL_INFX_RC_COLLECTION)
    DbtPy.bind_param(stmt, 4, c4, DbtPy.SQL_PARAM_INPUT, DbtPy.SQL_CHAR, DbtPy.SQL_INFX_RC_COLLECTION)
    DbtPy.bind_param(stmt, 5, c5, DbtPy.SQL_PARAM_INPUT, DbtPy.SQL_VARCHAR, DbtPy.SQL_INFX_RC_ROW)

    i = 0
    while i < 3:
        i += 1
        c1 = 100+i
        c2 = "SET{'Joe', 'Pheebes'}"
        c3 = "MULTISET{'1','2','3','4','5'}"
        c4 = "LIST{'10', '20', '30'}"
        c5 = "ROW('Pune', 'City', '411061')"
        DbtPy.execute(stmt, (c1, c2, c3, c4, c5));
   
    sql = "SELECT * FROM coll_param_tab"
    stmt = DbtPy.exec_immediate(conn, sql)
    tu = DbtPy.fetch_tuple(stmt)
    rc = 0
    while tu != False:
        rc += 1
        tu = DbtPy.fetch_tuple(stmt)

    print ("Collection Param data access complete")

#__END__
#__LUW_EXPECTED__
#Collection Param data access complete
#__ZOS_EXPECTED__
#Collection Param data access complete
#__SYSTEMI_EXPECTED__
#Collection Param data access complete
#__IDS_EXPECTED__
#Collection Param data access complete
