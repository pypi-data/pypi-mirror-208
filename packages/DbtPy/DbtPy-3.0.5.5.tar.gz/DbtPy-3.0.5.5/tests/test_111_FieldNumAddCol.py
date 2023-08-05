# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_111_FieldNumAddCol(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_111)

  def run_test_111(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    server = DbtPy.server_info( conn )
    if conn:
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)

      insert = "INSERT INTO animals values (7, 'cat', 'Benji', 5.1)"
      DbtPy.exec_immediate(conn, insert)
      
      stmt = DbtPy.exec_immediate(conn, "SELECT breed, COUNT(breed) AS number FROM animals GROUP BY breed ORDER BY breed")
    
      if (server.DBMS_NAME[0:3] == 'Inf'):
        num1 = DbtPy.field_num(stmt, "id")
        num2 = DbtPy.field_num(stmt, "breed")
        num3 = DbtPy.field_num(stmt, "number")
        num4 = DbtPy.field_num(stmt, "NUMBER")
        num5 = DbtPy.field_num(stmt, "bREED")
        num6 = DbtPy.field_num(stmt, 8)
        num7 = DbtPy.field_num(stmt, 1)
        num8 = DbtPy.field_num(stmt, "WEIGHT")
      else:
        num1 = DbtPy.field_num(stmt, "ID")
        num2 = DbtPy.field_num(stmt, "BREED")
        num3 = DbtPy.field_num(stmt, "NUMBER")
        num4 = DbtPy.field_num(stmt, "number")
        num5 = DbtPy.field_num(stmt, "Breed")
        num6 = DbtPy.field_num(stmt, 8)
        num7 = DbtPy.field_num(stmt, 1)
        num8 = DbtPy.field_num(stmt, "weight")
  
      print("%s" % num1)
      print("int(%d)" % num2)
      print("int(%d)" % num3)
      print("%s" % num4)
      
      print("%s" % num5)
      print("%s" % num6)
      print("int(%d)" % num7)
      print("%s" % num8)

      DbtPy.rollback(conn)
    else:
      print("Connection failed.")

#__END__
#__IDS_EXPECTED__
#False
#int(0)
#int(1)
#False
#False
#False
#int(1)
#False
