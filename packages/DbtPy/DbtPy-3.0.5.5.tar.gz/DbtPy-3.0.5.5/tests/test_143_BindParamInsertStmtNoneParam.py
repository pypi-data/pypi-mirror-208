# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_143_BindParamInsertStmtNoneParam(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_143)

  def run_test_143(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    
    DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)

    insert1 = "INSERT INTO animals (id, breed, name, weight) VALUES (NULL, 'ghost', NULL, ?)"
    select = 'SELECT id, breed, name, weight FROM animals WHERE weight IS NULL'
    
    if conn:
      stmt = DbtPy.prepare(conn, insert1)
    
      animal = None
      DbtPy.bind_param(stmt, 1, animal)
    
      if DbtPy.execute(stmt):
        stmt = DbtPy.exec_immediate(conn, select)
        row = DbtPy.fetch_tuple(stmt)
        while ( row ):
          #row.each { |child| print child }
          for i in row:
            print(i)
          row = DbtPy.fetch_tuple(stmt)

      DbtPy.rollback(conn)
    else:
      print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#None
#ghost
#None
#None
#__ZOS_EXPECTED__
#None
#ghost
#None
#None
#__SYSTEMI_EXPECTED__
#None
#ghost
#None
#None
#__IDS_EXPECTED__
#None
#ghost
#None
#None
