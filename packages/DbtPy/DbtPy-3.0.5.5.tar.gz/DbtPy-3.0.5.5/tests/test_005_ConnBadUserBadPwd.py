# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_005_ConnBadUserBadPwd(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_005)

  def run_test_005(self):
    baduser = "non_user"
    badpass = "invalid_password"
    dsn = "DATABASE=" + config.ConnStr + ";UID=" + baduser + ";PWD=" + badpass + ";"
    try:
      conn = DbtPy.connect(dsn, "", "")
      print("odd, DbtPy.connect succeeded with an invalid user / password")
      DbtPy.close(conn)
    except: 
      print("Ooops")

#__END__
#__LUW_EXPECTED__
#Ooops
#__ZOS_EXPECTED__
#Ooops
#__SYSTEMI_EXPECTED__
#Ooops
#__IDS_EXPECTED__
#Ooops
