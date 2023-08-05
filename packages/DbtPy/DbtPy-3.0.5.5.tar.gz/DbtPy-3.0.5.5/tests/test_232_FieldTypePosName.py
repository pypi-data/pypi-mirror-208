# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_232_FieldTypePosName(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_232)

  def run_test_232(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    result = DbtPy.exec_immediate(conn, "select * from sales")
     
    for i in range(0, DbtPy.num_fields(result) + 1):
      field_name = DbtPy.field_name(result,i)
      field_type = DbtPy.field_type(result, DbtPy.field_name(result,i))
      print(str(DbtPy.field_name(result, i)) + ":" + str(DbtPy.field_type(result, DbtPy.field_name(result, i))))
          
    print("-----")
    
    t = DbtPy.field_type(result,99)
    print(t)
    
    t1 = DbtPy.field_type(result, "HELMUT")
    print(t1)

#__END__
#__LUW_EXPECTED__
#SALES_DATE:date
#SALES_PERSON:string
#REGION:string
#SALES:int
#False:False
#-----
#False
#False
#__ZOS_EXPECTED__
#SALES_DATE:date
#SALES_PERSON:string
#REGION:string
#SALES:int
#False:False
#-----
#False
#False
#__SYSTEMI_EXPECTED__
#SALES_DATE:date
#SALES_PERSON:string
#REGION:string
#SALES:int
#False:False
#-----
#False
#False
#__IDS_EXPECTED__
#sales_date:date
#sales_person:string
#region:string
#sales:int
#False:False
#-----
#False
#False
