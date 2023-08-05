# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_103_NumFieldsSelect_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_103)

  def run_test_103(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
       result = DbtPy.exec_immediate(conn, "select * from org, project order by project.projname,org.deptnumb")
       cols = DbtPy.num_fields(result)
       j = 1
       row = DbtPy.fetch_tuple(result)
       while ( row ):
          print("%d) " % j)
          for i in range(0, cols):
             print("%s " % row[i])
          j += 1
          if (j > 10):
             break
          row = DbtPy.fetch_tuple(result)
       DbtPy.close(conn)
    else:
      print(DbtPy.conn_errormsg())

#__END__
#__IDS_EXPECTED__
#1) 10 Head Office 160 Corporate New York AD3113 ACCOUNT PROGRAMMING D21 000270 2.00 1982-01-01 1983-02-01 AD3110 
#2) 15 New England 50 Eastern Boston AD3113 ACCOUNT PROGRAMMING D21 000270 2.00 1982-01-01 1983-02-01 AD3110 
#3) 20 Mid Atlantic 10 Eastern Washington AD3113 ACCOUNT PROGRAMMING D21 000270 2.00 1982-01-01 1983-02-01 AD3110 
#4) 38 South Atlantic 30 Eastern Atlanta AD3113 ACCOUNT PROGRAMMING D21 000270 2.00 1982-01-01 1983-02-01 AD3110 
#5) 42 Great Lakes 100 Midwest Chicago AD3113 ACCOUNT PROGRAMMING D21 000270 2.00 1982-01-01 1983-02-01 AD3110 
#6) 51 Plains 140 Midwest Dallas AD3113 ACCOUNT PROGRAMMING D21 000270 2.00 1982-01-01 1983-02-01 AD3110 
#7) 66 Pacific 270 Western San Francisco AD3113 ACCOUNT PROGRAMMING D21 000270 2.00 1982-01-01 1983-02-01 AD3110 
#8) 84 Mountain 290 Western Denver AD3113 ACCOUNT PROGRAMMING D21 000270 2.00 1982-01-01 1983-02-01 AD3110 
#9) 10 Head Office 160 Corporate New York AD3100 ADMIN SERVICES D01 000010 6.50 1982-01-01 1983-02-01        
#10) 15 New England 50 Eastern Boston AD3100 ADMIN SERVICES D01 000010 6.50 1982-01-01 1983-02-01        