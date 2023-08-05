#

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_048_FetchTupleBinaryData_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_048)

  def run_test_048(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    if (not conn):
      print("Could not make a connection.") 
      return 0
    server = DbtPy.server_info( conn )
    
    fp = open("tests/spook_out.png", "wb")
    result = DbtPy.exec_immediate(conn, "SELECT picture FROM animal_pics WHERE name = 'Spook'")
    if (not result):
      print("Could not execute SELECT statement.")
      return 0
    row = DbtPy.fetch_tuple(result)
    if row:
      fp.write(row[0])
    else:
      print(DbtPy.stmt_errormsg())
    fp.close()
    cmp = (open('tests/spook_out.png', "rb").read() == open('tests/spook.png', "rb").read())
    print("Are the files the same:", cmp)

#__END__
#__LUW_EXPECTED__
#Are the files the same: True
#__ZOS_EXPECTED__
#Are the files the same: True
#__SYSTEMI_EXPECTED__
#Are the files the same: True
#__IDS_EXPECTED__
#Are the files the same: True
