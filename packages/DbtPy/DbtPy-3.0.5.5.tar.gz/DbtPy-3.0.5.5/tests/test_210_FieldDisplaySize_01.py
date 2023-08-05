# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_210_FieldDisplaySize_01(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_210)

  def run_test_210(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    result = DbtPy.exec_immediate(conn, "select * from staff")
    cols = DbtPy.num_fields(result)
    
    for i in range(0, cols):
      size = DbtPy.field_display_size(result,i)
      print("col:%d and size: %d" % (i, size))
    
    DbtPy.close(conn)

#__END__
#__LUW_EXPECTED__
#col:0 and size: 6
#col:1 and size: 9
#col:2 and size: 6
#col:3 and size: 5
#col:4 and size: 6
#col:5 and size: 9
#col:6 and size: 9
#__ZOS_EXPECTED__
#col:0 and size: 6
#col:1 and size: 9
#col:2 and size: 6
#col:3 and size: 5
#col:4 and size: 6
#col:5 and size: 9
#col:6 and size: 9
#__SYSTEMI_EXPECTED__
#col:0 and size: 6
#col:1 and size: 9
#col:2 and size: 6
#col:3 and size: 5
#col:4 and size: 6
#col:5 and size: 9
#col:6 and size: 9
#__IDS_EXPECTED__
#col:0 and size: 6
#col:1 and size: 9
#col:2 and size: 6
#col:3 and size: 5
#col:4 and size: 6
#col:5 and size: 9
#col:6 and size: 9
