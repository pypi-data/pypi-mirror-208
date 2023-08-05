# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_082_ConnWrongPwd(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_082)

  def run_test_082(self):
    try:
      conn = DbtPy.connect(config.ConnStr, config.user, "z")
      print("??? No way.")
    except:
      err = DbtPy.conn_error()
      print(err)

#__END__
#__IDS_EXPECTED__
#28000
