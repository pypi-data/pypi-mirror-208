# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_014_KeysetDrivenCursorNegativeRow(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_014)

  def run_test_014(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    serverinfo = DbtPy.server_info( conn )

    query = 'SELECT * FROM animals ORDER BY name'

    if (serverinfo.DBMS_NAME[0:3] != 'Inf'):
      stmt = DbtPy.prepare(conn, query, {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
    else:
      stmt = DbtPy.prepare(conn, query)
    DbtPy.execute(stmt)
    data = DbtPy.fetch_both( stmt )
    while ( data ):
      print("%s : %s : %s : %s\n" % (data[0], data[1], data[2], data[3]))
      data = DbtPy.fetch_both( stmt )
    try:
      stmt = DbtPy.prepare(conn, query, {DbtPy.SQL_ATTR_CURSOR_TYPE:  DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
      DbtPy.execute(stmt)
      rc = DbtPy.fetch_row(stmt, -1)
      print("Fetch row -1: %s" % str(rc))
    except:
      print("Requested row number must be a positive value")

    DbtPy.close(conn)

#__END__
#__LUW_EXPECTED__
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#1 : dog : Peaches          : 12.30
#0 : cat : Pook             : 3.20
#5 : goat : Rickety Ride     : 9.70
#2 : horse : Smarty           : 350.00
#6 : llama : Sweater          : 150.00
#Requested row number must be a positive value
#__ZOS_EXPECTED__
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#1 : dog : Peaches          : 12.30
#0 : cat : Pook             : 3.20
#5 : goat : Rickety Ride     : 9.70
#2 : horse : Smarty           : 350.00
#6 : llama : Sweater          : 150.00
#Requested row number must be a positive value
#__SYSTEMI_EXPECTED__
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#1 : dog : Peaches          : 12.30
#0 : cat : Pook             : 3.20
#5 : goat : Rickety Ride     : 9.70
#2 : horse : Smarty           : 350.00
#6 : llama : Sweater          : 150.00
#Requested row number must be a positive value
#__IDS_EXPECTED__
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#1 : dog : Peaches          : 12.30
#0 : cat : Pook             : 3.20
#5 : goat : Rickety Ride     : 9.70
#2 : horse : Smarty           : 350.00
#6 : llama : Sweater          : 150.00
#Requested row number must be a positive value
