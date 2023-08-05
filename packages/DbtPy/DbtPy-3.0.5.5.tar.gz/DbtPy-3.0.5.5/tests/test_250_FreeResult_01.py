# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_250_FreeResult_01(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_250)

  def run_test_250(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    result = DbtPy.exec_immediate(conn, "select * from sales")
    result2 = DbtPy.exec_immediate(conn, "select * from staff")
    result3 = DbtPy.exec_immediate(conn, "select * from emp_photo")
    
    r1 = DbtPy.free_result(result)
    r2 = DbtPy.free_result(result2)
    r3 = DbtPy.free_result(result3)
    
    print(r1)
    print(r2)
    print(r3)

#__END__
#__LUW_EXPECTED__
#True
#True
#True
#__ZOS_EXPECTED__
#True
#True
#True
#__SYSTEMI_EXPECTED__
#True
#True
#True
#__IDS_EXPECTED__
#True
#True
#True
