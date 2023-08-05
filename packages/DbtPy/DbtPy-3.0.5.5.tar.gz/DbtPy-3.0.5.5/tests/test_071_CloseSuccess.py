# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_071_CloseSuccess(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_071)

  def run_test_071(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      rc = DbtPy.close(conn)
      if (rc == True):
        print("DbtPy.close succeeded")
      else:
        print("DbtPy.close FAILED\n")
    else:
      print("%s" % DbtPy.conn_errormsg())
      print(",sqlstate=%s" % DbtPy.conn_error())
      print("%s" % DbtPy.conn_errormsg())
      print("%s" % DbtPy.conn_errormsg())
      print("%s" % DbtPy.conn_errormsg())
      print("%s" % DbtPy.conn_errormsg())

#__END__
#__LUW_EXPECTED__
#DbtPy.close succeeded
#__ZOS_EXPECTED__
#DbtPy.close succeeded
#__SYSTEMI_EXPECTED__
#DbtPy.close succeeded
#__IDS_EXPECTED__
#DbtPy.close succeeded
