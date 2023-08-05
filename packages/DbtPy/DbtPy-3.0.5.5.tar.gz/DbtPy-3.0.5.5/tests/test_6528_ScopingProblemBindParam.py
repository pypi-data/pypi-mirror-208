# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_6528_ScopingProblemBindParam(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_6528)

  def checked_ids_execute(self, stmt):
    DbtPy.execute(stmt)
    row = DbtPy.fetch_tuple(stmt)
    for i in row:
      print(i)

  def run_test_6528(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    server = DbtPy.server_info( conn )

    if conn:
      if (server.DBMS_NAME[0:3] == 'Inf'):
        sql = "SELECT TRIM(TRAILING FROM name) FROM animals WHERE breed = ?"
      else:
        sql = "SELECT RTRIM(name) FROM animals WHERE breed = ?"
      stmt = DbtPy.prepare(conn, sql)
      var = "cat"
      DbtPy.bind_param(stmt, 1, var, DbtPy.SQL_PARAM_INPUT)
      self.checked_ids_execute(stmt)
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#Pook
#__ZOS_EXPECTED__
#Pook
#__SYSTEMI_EXPECTED__
#Pook
#__IDS_EXPECTED__
#Pook
