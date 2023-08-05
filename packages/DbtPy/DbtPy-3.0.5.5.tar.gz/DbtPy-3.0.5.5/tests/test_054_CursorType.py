#

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_054_CursorType(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_054)

  def run_test_054(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    serverinfo = DbtPy.server_info( conn )

    stmt = DbtPy.exec_immediate(conn, "SELECT * FROM animals")
    val = DbtPy.get_option(stmt, DbtPy.SQL_ATTR_CURSOR_TYPE, 0)
    print(val)

    op = {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_FORWARD_ONLY}
    stmt = DbtPy.exec_immediate(conn, "SELECT * FROM animals", op)
    val = DbtPy.get_option(stmt, DbtPy.SQL_ATTR_CURSOR_TYPE, 0)
    print(val)

    op = {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_KEYSET_DRIVEN}
    stmt = DbtPy.exec_immediate(conn, "SELECT * FROM animals", op)
    val = DbtPy.get_option(stmt, DbtPy.SQL_ATTR_CURSOR_TYPE, 0)
    print(val)

    op = {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_STATIC}
    stmt = DbtPy.exec_immediate(conn, "SELECT * FROM animals", op)
    val = DbtPy.get_option(stmt, DbtPy.SQL_ATTR_CURSOR_TYPE, 0)
    print(val)

#__END__
#__IDS_EXPECTED__
#0
#0
#0
#0
#
