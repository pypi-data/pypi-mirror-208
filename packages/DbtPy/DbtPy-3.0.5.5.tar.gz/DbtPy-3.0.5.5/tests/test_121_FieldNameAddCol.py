# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_121_FieldNameAddCol(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_121)

  def run_test_121(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    server = DbtPy.server_info( conn )
    
    if conn:
      DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)

      insert = "INSERT INTO animals values (7, 'cat', 'Benji', 5.1)"
      DbtPy.exec_immediate(conn, insert)
        
      stmt = DbtPy.exec_immediate(conn, "SELECT breed, COUNT(breed) AS number FROM animals GROUP BY breed ORDER BY breed")
    
      name1 = DbtPy.field_name(stmt, 0)
      name2 = DbtPy.field_name(stmt, 1)
      name3 = DbtPy.field_name(stmt, 2)
      name4 = DbtPy.field_name(stmt, 3)
      
      if (server.DBMS_NAME[0:3] == 'Inf'):
        name5 = DbtPy.field_name(stmt, "breed")
        name6 = DbtPy.field_name(stmt, 7)
        name7 = DbtPy.field_name(stmt, '"nUMBER"')
        name8 = DbtPy.field_name(stmt, "number")
      else:
        name5 = DbtPy.field_name(stmt, "BREED")
        name6 = DbtPy.field_name(stmt, 7)
        name7 = DbtPy.field_name(stmt, '"Number"')
        name8 = DbtPy.field_name(stmt, "NUMBER")
      
      print("string(%d) \"%s\"" % (len(name1), name1))
      print("string(%d) \"%s\"" % (len(name2), name2))
      print("%s" % name3)
      print("%s" % name4)

      print("string(%d) \"%s\"" % (len(name5), name5))
      print("%s" % name6)
      print("%s" % name7)
      print("string(%d) \"%s\"" % (len(name8), name8))

      DbtPy.rollback(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#string(5) "BREED"
#string(6) "NUMBER"
#False
#False
#string(5) "BREED"
#False
#False
#string(6) "NUMBER"
#__ZOS_EXPECTED__
#string(5) "BREED"
#string(6) "NUMBER"
#False
#False
#string(5) "BREED"
#False
#False
#string(6) "NUMBER"
#__SYSTEMI_EXPECTED__
#string(5) "BREED"
#string(6) "NUMBER"
#False
#False
#string(5) "BREED"
#False
#False
#string(6) "NUMBER"
#__IDS_EXPECTED__
#string(5) "breed"
#string(6) "number"
#False
#False
#string(5) "breed"
#False
#False
#string(6) "number"
