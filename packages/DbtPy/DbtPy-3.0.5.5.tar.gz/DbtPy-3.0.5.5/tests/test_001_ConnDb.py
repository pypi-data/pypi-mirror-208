# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_001_ConnDb(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_001)

  def run_test_001(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      
    if conn:
      print("Connection succeeded.")
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#Connection succeeded.
#__ZOS_EXPECTED__
#Connection succeeded.
#__SYSTEMI_EXPECTED__
#Connection succeeded.
#__IDS_EXPECTED__
#Connection succeeded.
