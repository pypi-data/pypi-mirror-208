# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_034_FetchAssoc(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_034)

  def run_test_034(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    server = DbtPy.server_info( conn )
    op = {DbtPy.ATTR_CASE: DbtPy.CASE_UPPER}
    DbtPy.set_option(conn, op, 1)

    result = DbtPy.exec_immediate(conn, "select * from staff")
    row = DbtPy.fetch_assoc(result)
    if( row ):
      #printf("%5d  ",row['ID'])
      #printf("%-10s ",row['NAME'])
      #printf("%5d ",row['DEPT'])
      #printf("%-7s ",row['JOB'])
      #printf("%5d ", row['YEARS'])
      #printf("%15s ", row['SALARY'])
      #printf("%10s ", row['COMM'])
      #puts ""
      print("%5d %-10s %5d %-7s %5d %15s %10s" % (row['ID'], row['NAME'], row['DEPT'], row['JOB'], row['YEARS'], row['SALARY'], row['COMM']))
    
    DbtPy.close(conn)

#__END__
#__LUW_EXPECTED__
#   10 Sanders       20 Mgr         7        18357.50       None
#__ZOS_EXPECTED__
#   10 Sanders       20 Mgr         7        18357.50       None
#__SYSTEMI_EXPECTED__
#   10 Sanders       20 Mgr         7        18357.50       None
#__IDS_EXPECTED__
#   10 Sanders       20 Mgr         7        18357.50       None
