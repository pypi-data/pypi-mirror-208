# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_063_Tables_04(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_063)

  def run_test_063(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      
    result = DbtPy.tables(conn, None, "SYSIBM", "", "VIEW")
    
    if (type(result) == DbtPy.IFXStatement):
      print("Resource is a IFX Statement")
      
    DbtPy.free_result(result)

#__END__
#__IDS_EXPECTED__
#Resource is a IFX Statement
