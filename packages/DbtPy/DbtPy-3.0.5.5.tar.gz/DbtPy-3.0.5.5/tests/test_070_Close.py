# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_070_Close(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_070)

  def run_test_070(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    if conn:
      if (type(conn) == DbtPy.IFXConnection):
        print("Resource is a Ifx Connection")
      
      rc = DbtPy.close(conn)
      
      print(rc)
    else:
      print("Connection failed.")

#__END__
#__IDS_EXPECTED__
#Resource is a Ifx Connection
#True
