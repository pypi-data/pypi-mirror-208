# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_211_FieldDisplaySize_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_211)

  def run_test_211(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    result = DbtPy.exec_immediate(conn, "select * from sales")
    
    i = 1
    
    while (i <= DbtPy.num_fields(result)):
      #printf("%d size %d\n",i, DbtPy.field_display_size(result,i) || 0)
      print("%d size %d" % (i, DbtPy.field_display_size(result,i) or 0))
      i += 1
    
    DbtPy.close(conn)

#__END__
#__LUW_EXPECTED__
#1 size 15
#2 size 15
#3 size 11
#4 size 0
#__ZOS_EXPECTED__
#1 size 15
#2 size 15
#3 size 11
#4 size 0
#__SYSTEMI_EXPECTED__
#1 size 15
#2 size 15
#3 size 11
#4 size 0
#__IDS_EXPECTED__
#1 size 15
#2 size 15
#3 size 11
#4 size 0
