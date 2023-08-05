# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_102_NumFieldsSelect_01(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_102)

  def run_test_102(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if (not conn):
      print(DbtPy.conn_errormsg())
    
    server = DbtPy.server_info( conn )
    if ((server.DBMS_NAME[0:2] != "AS") and (server.DBMS_NAME != "DB2") and (server.DBMS_NAME[0:3] != "Inf")):
      result = DbtPy.exec_immediate(conn, "VALUES(1)")
      #throw :unsupported unless result
      if (not result):
        raise Exception('Unsupported')
      print(DbtPy.num_fields(result))
    else:
      print('1')
    DbtPy.close(conn)

#__END__
#__LUW_EXPECTED__
#1
#__ZOS_EXPECTED__
#1
#__SYSTEMI_EXPECTED__
#1
#__IDS_EXPECTED__
#1
