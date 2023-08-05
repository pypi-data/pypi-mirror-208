# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_251_FreeResult_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_251)

  def run_test_251(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    result = DbtPy.exec_immediate(conn, "select * from sales")
    
    r1 = DbtPy.free_result(result)
    r2 = DbtPy.free_result(result)
    r3 = ''
    try:
      r3 = DbtPy.free_result(result99)
    except:
      r3 = None
    
    print(r1)
    print(r2)
    print(r3)

#__END__
#__LUW_EXPECTED__
#True
#True
#None
#__ZOS_EXPECTED__
#True
#True
#None
#__SYSTEMI_EXPECTED__
#True
#True
#None
#__IDS_EXPECTED__
#True
#True
#None
