# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_013_KeysetDrivenCursorSelect02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_013)

  def run_test_013(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      
    if conn:
      serverinfo = DbtPy.server_info( conn )
      if (serverinfo.DBMS_NAME[0:3] != 'Inf'):
        stmt = DbtPy.prepare(conn, "SELECT name FROM animals WHERE weight < 10.0", {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
      else:
        stmt = DbtPy.prepare(conn, "SELECT name FROM animals WHERE weight < 10.0")
      DbtPy.execute(stmt)
      data = DbtPy.fetch_both( stmt )
      while (data):
        print(data[0])
        data = DbtPy.fetch_both( stmt )
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#Pook            
#Bubbles         
#Gizmo           
#Rickety Ride    
#__ZOS_EXPECTED__
#Pook            
#Bubbles         
#Gizmo           
#Rickety Ride    
#__SYSTEMI_EXPECTED__
#Pook            
#Bubbles         
#Gizmo           
#Rickety Ride    
#__IDS_EXPECTED__
#Pook            
#Bubbles         
#Gizmo           
#Rickety Ride    
