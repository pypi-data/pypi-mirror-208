#

#

#

import unittest, sys, os
import DbtPy
#need to add this line below to each file to make the connect parameters available to all the test files
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_313_Collection(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_313)

  def run_test_313(self):
    # Make a connection
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    # Get the server type
    server = DbtPy.server_info( conn )

    try:
        sql = "drop table collection_tab;"
        stmt = DbtPy.exec_immediate(conn, sql)
    except:
         pass
  
    SetupSqlSet = [
        "create table collection_tab ( col1 int, s1 SET(float not null), m1  MULTISET(char(20) not null), l1 LIST(bigint not null)) ;",
        "insert into collection_tab values( 1, SET{11.10, 12.11},  MULTISET{'Hey', 'Hell'}, LIST{120, -120});",
        "insert into collection_tab values( 2, SET{13.11, 14.20},  MULTISET{'Jhon', 'Nick'}, LIST{130, -130});",
        "insert into collection_tab values( 3, SET{14.21, 14.00},  MULTISET{'Dave', 'Mill'}, LIST{140, -141});",
        "insert into collection_tab values( 4, SET{15.0, 16},      MULTISET{'Mon', 'Phebee'}, LIST{150, -150});"
    ]

    i = 0
    for sql in SetupSqlSet:
        i += 1
        stmt = DbtPy.exec_immediate(conn, sql)

    sql = "select * from collection_tab;"
    stmt =  DbtPy.exec_immediate(conn, sql)
    tu = DbtPy.fetch_tuple(stmt)
    rc = 0
    while tu != False:
        rc += 1
        tu = DbtPy.fetch_tuple(stmt)

    print ("Collection Data Access complete")

#__END__
#__LUW_EXPECTED__
#Collection Data Access complete
#__ZOS_EXPECTED__
#Collection Data Access complete
#__SYSTEMI_EXPECTED__
#Collection Data Access complete
#__IDS_EXPECTED__
#Collection Data Access complete


