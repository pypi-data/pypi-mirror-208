# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_092_ConnmsgWrongPwd(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_092)

  def run_test_092(self):
    try:
      conn = DbtPy.connect(config.ConnStr, config.user, "z")
      print("??? No way.")
    except:
      err = DbtPy.conn_errormsg()
      print(err[0:68])

#__END__
#__IDS_EXPECTED__
#[GBasedbt][GBase ODBC Driver][GBasedbt]Incorrect password or user
