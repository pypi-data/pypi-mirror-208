# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_081_ConnWrongUser(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_081)

  def run_test_081(self):
    try:
      conn = DbtPy.connect(config.ConnStr, "y", config.password)
      print("??? No way.")
    except:
      print(DbtPy.conn_error())

    #if conn:
    #  print "??? No way."
    #else:
    #  err = DbtPy.conn_error 
    #  print err

#__END__
#__IDS_EXPECTED__
#28000