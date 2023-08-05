# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_241_FieldWidthPosName_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_241)

  def run_test_241(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    result = DbtPy.exec_immediate(conn, "select * from sales")
    result2 = DbtPy.exec_immediate(conn, "select * from staff")
    result3 = DbtPy.exec_immediate(conn, "select * from emp_photo")
    
    for i in range(0, DbtPy.num_fields(result)):
      print(str(DbtPy.field_width(result,i)))
    
    print("\n-----")
    
    for i in range(0, DbtPy.num_fields(result2)):
      print(str(DbtPy.field_width(result2,DbtPy.field_name(result2,i))))

#__END__
#__LUW_EXPECTED__
#10
#15
#15
#11
#
#-----
#6
#9
#6
#5
#6
#9
#9
#__ZOS_EXPECTED__
#10
#15
#15
#11
#
#-----
#6
#9
#6
#5
#6
#9
#9
#__SYSTEMI_EXPECTED__
#10
#15
#15
#11
#
#-----
#6
#9
#6
#5
#6
#9
#9
#__IDS_EXPECTED__
#6
#15
#15
#4
#
#-----
#2
#9
#2
#5
#2
#9
#9
