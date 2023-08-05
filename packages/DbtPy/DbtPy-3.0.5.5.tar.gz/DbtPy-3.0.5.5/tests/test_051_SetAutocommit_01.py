# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_051_SetAutocommit_01(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_051)

  def run_test_051(self):
    options = { DbtPy.SQL_ATTR_AUTOCOMMIT:  DbtPy.SQL_AUTOCOMMIT_OFF }
      
    conn = DbtPy.connect(config.ConnStr, config.user, config.password, options)
      
    ac = DbtPy.autocommit(conn)
      
    print(ac)

#__END__
#__LUW_EXPECTED__
#0
#__ZOS_EXPECTED__
#0
#__SYSTEMI_EXPECTED__
#0
#__IDS_EXPECTED__
#0
