#

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_045_FetchTupleBinaryData_01(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_045)
    
  def run_test_045(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    fp = open("tests/pic1_out.jpg", "wb")
    result = DbtPy.exec_immediate(conn, "SELECT picture FROM animal_pics WHERE name = 'Helmut'")
    row = DbtPy.fetch_tuple(result)
    if row:
      fp.write(row[0])
    else:
      print(DbtPy.stmt_errormsg())
    fp.close()
    cmp = (open('tests/pic1_out.jpg', 'rb').read() == open('tests/pic1.jpg', 'rb').read())
    print('Are the files the same:', cmp)


#__END__
#__LUW_EXPECTED__
#Are the files the same: True
#__ZOS_EXPECTED__
#Are the files the same: True
#__SYSTEMI_EXPECTED__
#Are the files the same: True
#__IDS_EXPECTED__
#Are the files the same: True
