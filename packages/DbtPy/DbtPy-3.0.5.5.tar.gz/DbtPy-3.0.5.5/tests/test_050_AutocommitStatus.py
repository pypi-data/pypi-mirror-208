# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_050_AutocommitStatus(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_050)

  def run_test_050(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
     
    ac = DbtPy.autocommit(conn)
      
    print(ac)

#__END__
#__LUW_EXPECTED__
#1
#__ZOS_EXPECTED__
#1
#__SYSTEMI_EXPECTED__
#1
#__IDS_EXPECTED__
#1
