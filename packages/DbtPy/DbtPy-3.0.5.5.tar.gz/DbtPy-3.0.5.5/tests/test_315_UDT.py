#

#

#

import unittest, sys, os
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):
    def test_315_UDT(self):
        obj = DbtPyTestFunctions()
        obj.assert_expect(self.run_test_315)

    def run_test_315(self):
        conn = DbtPy.connect(config.ConnStr, config.user, config.password)

        server = DbtPy.server_info( conn )

        try:
            sql = "drop table t31;"
            stmt = DbtPy.exec_immediate(conn, sql)
        except:
            pass

        sql = "DROP ROW TYPE if exists udt_t4 RESTRICT;"
        DbtPy.exec_immediate(conn, sql)

        sql = " create ROW type udt_t4 (a int);"
        stmt = DbtPy.exec_immediate(conn, sql)

        SetupSqlSet = [
            "create table t31 ( c1 int, c2 char(20), c3 int, c4 udt_t4 ) ;",
            "insert into t31 values( 1, 'Sunday', 101, (ROW(201)::udt_t4) );",
            "insert into t31 values( 2, 'Monday', 102, (ROW(202)::udt_t4) );"
        ]

        i = 0
        for sql in SetupSqlSet:
            i += 1
            stmt = DbtPy.exec_immediate(conn, sql)

        # The first record executed is for create table
        i -= 1

        # Select records
        sql = "SELECT * FROM t31"
        stmt = DbtPy.exec_immediate(conn, sql)
        dictionary = DbtPy.fetch_both(stmt)

        print("UDT complete")

#__END__
#__LUW_EXPECTED__
#UDT complete
#__ZOS_EXPECTED__
#UDT complete
#__SYSTEMI_EXPECTED__
#UDT complete
#__IDS_EXPECTED__
#UDT complete
