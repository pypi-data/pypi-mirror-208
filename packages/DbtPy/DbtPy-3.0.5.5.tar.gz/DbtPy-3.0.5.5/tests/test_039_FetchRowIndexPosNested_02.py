# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_039_FetchRowIndexPosNested_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_039)

  def run_test_039(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    serverinfo = DbtPy.server_info( conn )

    if (serverinfo.DBMS_NAME[0:3] != 'Inf'):
      result = DbtPy.prepare(conn, "SELECT * FROM animals", {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
    else:
      result = DbtPy.prepare(conn, "SELECT * FROM animals")
    DbtPy.execute(result)
    row = DbtPy.fetch_row(result)
    while ( row ):
      if (serverinfo.DBMS_NAME[0:3] != 'Inf'):
        result2 = DbtPy.prepare(conn, "SELECT * FROM animals", {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
      else:
        result2 = DbtPy.prepare(conn, "SELECT * FROM animals")
      DbtPy.execute(result2)
      while (DbtPy.fetch_row(result2)):
        print("%s : %s : %s : %s" % (DbtPy.result(result2, 0), \
                                     DbtPy.result(result2, 1), \
                                     DbtPy.result(result2, 2), \
                                     DbtPy.result(result2, 3)))
      row = DbtPy.fetch_row(result)

#__END__
#__LUW_EXPECTED__
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#__ZOS_EXPECTED__
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#__SYSTEMI_EXPECTED__
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#__IDS_EXPECTED__
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
#0 : cat : Pook             : 3.20
#1 : dog : Peaches          : 12.30
#2 : horse : Smarty           : 350.00
#3 : gold fish : Bubbles          : 0.10
#4 : budgerigar : Gizmo            : 0.20
#5 : goat : Rickety Ride     : 9.70
#6 : llama : Sweater          : 150.00
