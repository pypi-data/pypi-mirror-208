# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_120_FieldName(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_120)

  def run_test_120(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    server = DbtPy.server_info( conn )

    if conn:
      stmt = DbtPy.exec_immediate(conn, "SELECT * FROM animals")
    
      name1 = DbtPy.field_name(stmt, 1)
      name2 = DbtPy.field_name(stmt, 2)
      name3 = DbtPy.field_name(stmt, 3)
      name4 = DbtPy.field_name(stmt, 4)
      name6 = DbtPy.field_name(stmt, 8)
      name7 = DbtPy.field_name(stmt, 0)
      
      if (server.DBMS_NAME[0:3] == 'Inf'):
        name5 = DbtPy.field_name(stmt, "id")
        name8 = DbtPy.field_name(stmt, "WEIGHT")
      else:
        name5 = DbtPy.field_name(stmt, "ID")
        name8 = DbtPy.field_name(stmt, "weight")

      print("string(%d) \"%s\"" % (len(name1), name1))
      print("string(%d) \"%s\"" % (len(name2), name2))
      print("string(%d) \"%s\"" % (len(name3), name3))
      print("%s" % name4)

      print("string(%d) \"%s\"" % (len(name5), name5))
      print("%s" % name6)
      print("string(%d) \"%s\"" % (len(name7), name7))
      print("%s" % name8)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#string(5) "BREED"
#string(4) "NAME"
#string(6) "WEIGHT"
#False
#string(2) "ID"
#False
#string(2) "ID"
#False
#__ZOS_EXPECTED__
#string(5) "BREED"
#string(4) "NAME"
#string(6) "WEIGHT"
#False
#string(2) "ID"
#False
#string(2) "ID"
#False
#__SYSTEMI_EXPECTED__
#string(5) "BREED"
#string(4) "NAME"
#string(6) "WEIGHT"
#False
#string(2) "ID"
#False
#string(2) "ID"
#False
#__IDS_EXPECTED__
#string(5) "breed"
#string(4) "name"
#string(6) "weight"
#False
#string(2) "id"
#False
#string(2) "id"
#False
