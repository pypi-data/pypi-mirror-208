# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_212_FieldDisplaySize_03(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_212)

  def run_test_212(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    server = DbtPy.server_info( conn )

    result = DbtPy.exec_immediate(conn, "select * from sales")
    
    if (server.DBMS_NAME[0:3] == 'Inf'):
      i = "sales_person"
    else:
      i = "SALES_PERSON"
    
    print("%s size %d" % (i, DbtPy.field_display_size(result,i)))
    
    i = 2
    print("%d size %d" % (i, DbtPy.field_display_size(result,i)))

#__END__
#__LUW_EXPECTED__
#SALES_PERSON size 15
#2 size 15
#__ZOS_EXPECTED__
#SALES_PERSON size 15
#2 size 15
#__SYSTEMI_EXPECTED__
#SALES_PERSON size 15
#2 size 15
#__IDS_EXPECTED__
#sales_person size 15
#2 size 15
