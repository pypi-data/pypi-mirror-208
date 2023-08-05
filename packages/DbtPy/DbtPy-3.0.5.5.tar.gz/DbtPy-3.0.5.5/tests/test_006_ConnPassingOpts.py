# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):
  
  def test_006_ConnPassingOpts(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_006)
	  
  def run_test_006(self):    

    options1 = {DbtPy.SQL_ATTR_CURSOR_TYPE:  DbtPy.SQL_CURSOR_KEYSET_DRIVEN}
    options2 = {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_FORWARD_ONLY}
      
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
  
    if conn:
      serverinfo = DbtPy.server_info( conn )

      if (serverinfo.DBMS_NAME[0:3] == 'Inf'):
        options1 = options2

      stmt = DbtPy.prepare(conn, "SELECT name FROM animals WHERE weight < 10.0", options2)
      DbtPy.execute(stmt)
      data = DbtPy.fetch_both(stmt)
      while ( data ):
        print(data[0])
        data = DbtPy.fetch_both(stmt)
      
      print("")

      stmt = DbtPy.prepare(conn, "SELECT name FROM animals WHERE weight < 10.0", options1)
      DbtPy.execute(stmt)
      data = DbtPy.fetch_both(stmt)
      while ( data ):
        print(data[0])
        data = DbtPy.fetch_both(stmt)
    
      DbtPy.close(conn)
    else:
      print("Connection failed.")

#__END__
#__IDS_EXPECTED__
#Pook            
#Bubbles         
#Gizmo           
#Rickety Ride    
#
#Pook            
#Bubbles         
#Gizmo           
#Rickety Ride    
