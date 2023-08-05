# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_032_ResultIndexName(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_032)

  def run_test_032(self):
      conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      server = DbtPy.server_info( conn )

      if conn:
        stmt = DbtPy.exec_immediate(conn, "SELECT id, breed, name, weight FROM animals WHERE id = 6")
        
        while (DbtPy.fetch_row(stmt)):
          id = DbtPy.result(stmt, "id")
          breed = DbtPy.result(stmt, "breed")
          name = DbtPy.result(stmt, "name")
          weight = DbtPy.result(stmt, "weight")
          print("int(%d)" % id)
          print("string(%d) \"%s\"" % (len(breed), breed))
          print("string(%d) \"%s\"" % (len(name), name))
          print("string(%d) \"%s\"" % (len(str(weight)), weight))
        DbtPy.close(conn)
      else:
        print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#int(6)
#string(5) "llama"
#string(16) "Sweater         "
#string(6) "150.00"
#__ZOS_EXPECTED__
#int(6)
#string(5) "llama"
#string(16) "Sweater         "
#string(6) "150.00"
#__SYSTEMI_EXPECTED__
#int(6)
#string(5) "llama"
#string(16) "Sweater         "
#string(6) "150.00"
#__IDS_EXPECTED__
#int(6)
#string(5) "llama"
#string(16) "Sweater         "
#string(6) "150.00"
