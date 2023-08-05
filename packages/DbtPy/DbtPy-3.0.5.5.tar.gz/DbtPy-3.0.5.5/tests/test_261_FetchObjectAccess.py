# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_261_FetchObjectAccess(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_261)

  def run_test_261(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    server = DbtPy.server_info( conn )
    if (server.DBMS_NAME[0:3] == 'Inf'):
      op = {DbtPy.ATTR_CASE: DbtPy.CASE_UPPER}
      DbtPy.set_option(conn, op, 1)

    if (server.DBMS_NAME[0:3] == 'Inf'):
      sql = "SELECT breed, TRIM(TRAILING FROM name) AS name FROM animals WHERE id = ?"
    else:
      sql = "SELECT breed, RTRIM(name) AS name FROM animals WHERE id = ?"

    if conn:
      stmt = DbtPy.prepare(conn, sql)
      DbtPy.execute(stmt, (0,))

#      NOTE: This is a workaround
#      function fetch_object() to be implemented...
#      pet = DbtPy.fetch_object(stmt)
#      while (pet):
#          print "Come here, %s, my little %s!" % (pet.NAME, pet.BREED)
#          pet = DbtPy.fetch_object(stmt)
      
      class Pet:
          pass
      
      data = DbtPy.fetch_assoc(stmt)
      while ( data ):
         pet = Pet()
         pet.NAME = data['NAME']
         pet.BREED = data['BREED']
         print("Come here, %s, my little %s!" % (pet.NAME, pet.BREED))
         data = DbtPy.fetch_assoc(stmt)
         
      DbtPy.close(conn)
      
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#Come here, Pook, my little cat!
#__ZOS_EXPECTED__
#Come here, Pook, my little cat!
#__SYSTEMI_EXPECTED__
#Come here, Pook, my little cat!
#__IDS_EXPECTED__
#Come here, Pook, my little cat!
