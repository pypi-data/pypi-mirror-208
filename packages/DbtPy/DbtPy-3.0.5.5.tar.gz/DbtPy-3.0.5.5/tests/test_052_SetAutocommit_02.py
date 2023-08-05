# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_052_SetAutocommit_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_052)
	  
  def run_test_052(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      
    DbtPy.autocommit(conn, 0)
      
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
