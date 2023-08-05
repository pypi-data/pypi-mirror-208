# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_018_selectRowcountPrefetchSetOpt(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_018)

  def run_test_018(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_ON)
    if conn:
      stmt = DbtPy.prepare(conn, "SELECT * from animals WHERE weight < 10.0" )
      DbtPy.set_option(stmt, {DbtPy.SQL_ATTR_ROWCOUNT_PREFETCH : DbtPy.SQL_ROWCOUNT_PREFETCH_ON}, 2)
      result = DbtPy.execute(stmt)
      if result:
        rows = DbtPy.num_rows(stmt)
        print("affected row:", rows)
        DbtPy.free_result(stmt)
      else:
        print(DbtPy.stmt_errormsg())

      DbtPy.set_option(stmt, {DbtPy.SQL_ATTR_ROWCOUNT_PREFETCH : DbtPy.SQL_ROWCOUNT_PREFETCH_OFF}, 2)
      result = DbtPy.execute(stmt)
      if result:
        rows = DbtPy.num_rows(stmt)
        print("affected row:", rows)
        DbtPy.free_result(stmt)
      else:
        print(DbtPy.stmt_errormsg())

      DbtPy.set_option(stmt, {DbtPy.SQL_ATTR_ROWCOUNT_PREFETCH : DbtPy.SQL_ROWCOUNT_PREFETCH_ON}, 2)
      result = DbtPy.execute(stmt)
      if result:
        rows = DbtPy.num_rows(stmt)
        print("affected row:", rows)
      else:
        print(DbtPy.stmt_errormsg())

      DbtPy.close(conn)
    else:
      print("no connection:", DbtPy.conn_errormsg())

#__END__
#__LUW_EXPECTED__
#affected row: 4
#affected row: -1
#affected row: 4
#__ZOS_EXPECTED__
#affected row: 4
#affected row: -1
#affected row: 4
#__SYSTEMI_EXPECTED__
#affected row: 4
#affected row: -1
#affected row: 4
#__IDS_EXPECTED__
#affected row: 4
#affected row: -1
#affected row: 4
