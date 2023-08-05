# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_038_FetchRowIndexPosNested_01(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_038)

  def run_test_038(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    serverinfo = DbtPy.server_info( conn )

    if (serverinfo.DBMS_NAME[0:3] != 'Inf'):
      result = DbtPy.exec_immediate(conn, "SELECT * FROM staff WHERE id < 101", {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
    else:
      result = DbtPy.exec_immediate(conn, "SELECT * FROM staff WHERE id < 101")

    row = DbtPy.fetch_row(result)
    while ( row ):
      if (serverinfo.DBMS_NAME[0:3] != 'Inf'):
        result2 = DbtPy.prepare(conn, "SELECT * FROM staff WHERE id < 101", {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
      else:
        result2 = DbtPy.prepare(conn, "SELECT * FROM staff WHERE id < 101")
      DbtPy.execute(result2)
      row2 = DbtPy.fetch_row(result2)
      while ( row2 ):
        print("%s : %s : %s : %s : %s\n" % (DbtPy.result(result2, 0), \
                                            DbtPy.result(result2, 1), \
                                            DbtPy.result(result2, 2), \
                                            DbtPy.result(result2, 3), \
                                            DbtPy.result(result2, 5)))
        row2 = DbtPy.fetch_row(result2)
      row = DbtPy.fetch_row(result)

#__END__
#__LUW_EXPECTED__
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#__ZOS_EXPECTED__
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#__SYSTEMI_EXPECTED__
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#__IDS_EXPECTED__
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
#10 : Sanders : 20 : Mgr   : 18357.50
#20 : Pernal : 20 : Sales : 18171.25
#30 : Marenghi : 38 : Mgr   : 17506.75
#40 : OBrien : 38 : Sales : 18006.00
#50 : Hanes : 15 : Mgr   : 20659.80
#60 : Quigley : 38 : Sales : 16808.30
#70 : Rothman : 15 : Sales : 16502.83
#80 : James : 20 : Clerk : 13504.60
#90 : Koonitz : 42 : Sales : 18001.75
#100 : Plotz : 42 : Mgr   : 18352.80
