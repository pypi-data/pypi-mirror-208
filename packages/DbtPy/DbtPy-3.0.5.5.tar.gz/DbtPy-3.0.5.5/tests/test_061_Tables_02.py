# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_061_Tables_02(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_061)

  def run_test_061(self):
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
    
    if conn:
      server = DbtPy.server_info( conn )
      op = {DbtPy.ATTR_CASE: DbtPy.CASE_UPPER}
      DbtPy.set_option(conn, op, 1)

      result = DbtPy.tables(conn, None, 't');
      i = 0
      row = DbtPy.fetch_both(result)
      while ( row ):
        str = row['TABLE_SCHEM'] + row['TABLE_NAME'] + row['TABLE_TYPE']
        if (i < 4):
          print(str)
        i = i + 1
        row = DbtPy.fetch_both(result)

      DbtPy.exec_immediate(conn, 'DROP TABLE t.t1')
      DbtPy.exec_immediate(conn, 'DROP TABLE t.t2')
      DbtPy.exec_immediate(conn, 'DROP TABLE t.t3')
      DbtPy.exec_immediate(conn, 'DROP TABLE t.t4')

      print("done!")
    else:
      print("no connection: %s" % DbtPy.conn_errormsg())

#__END__
#__IDS_EXPECTED__
#tt1TABLE
#tt2TABLE
#tt3TABLE
#tt4TABLE
#done!
