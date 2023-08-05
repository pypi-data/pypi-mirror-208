# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_064_Tables_05(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_064)

  def run_test_064(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    server = DbtPy.server_info( conn )

    create = 'CREATE SCHEMA AUTHORIZATION t'
    try:
      result = DbtPy.exec_immediate(conn, create)
    except:
      pass
    
    create = 'CREATE TABLE t.t1( c1 integer, c2 varchar(40))'
    try:
      result = DbtPy.exec_immediate(conn, create)
    except:
      pass
    
    create = 'CREATE TABLE t.t2( c1 integer, c2 varchar(40))'
    try:
      result = DbtPy.exec_immediate(conn, create)
    except:
      pass
    
    create = 'CREATE TABLE t.t3( c1 integer, c2 varchar(40))'
    try:
      result = DbtPy.exec_immediate(conn, create)
    except:
      pass
    
    create = 'CREATE TABLE t.t4( c1 integer, c2 varchar(40))'
    try:
      result = DbtPy.exec_immediate(conn, create)
    except:
      pass
    
    result = DbtPy.tables(conn, None, 't')
    
    for i in range(0, DbtPy.num_fields(result)):
      print("%s, " % DbtPy.field_name(result, i))
    print()
    print()
  
    i = 0
    row = DbtPy.fetch_tuple(result)
    while ( row ):
      DbtPy.num_fields(result)
      if (i < 4):
        print(", " + row[1] + ", " + row[2] + ", " + row[3] + ", ,\n")
      i = i + 1
      row = DbtPy.fetch_tuple(result)

    DbtPy.free_result(result)

    DbtPy.exec_immediate(conn, 'DROP TABLE t.t1')
    DbtPy.exec_immediate(conn, 'DROP TABLE t.t2')
    DbtPy.exec_immediate(conn, 'DROP TABLE t.t3')
    DbtPy.exec_immediate(conn, 'DROP TABLE t.t4')

#__END__ 
#__IDS_EXPECTED__
#TABLE_CAT, TABLE_SCHEM, TABLE_NAME, TABLE_TYPE, REMARKS, 
#
#, t, t1, TABLE, ,
#, t, t2, TABLE, ,
#, t, t3, TABLE, ,
#, t, t4, TABLE, ,
