# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_049_InsertNoneParam(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_049)
	  
  def run_test_049(self):      
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)
      
    insert = "INSERT INTO animals (id, breed, name, weight) VALUES (?, ?, ?, ?)"
    select = 'SELECT id, breed, name, weight FROM animals WHERE weight IS NULL'
      
    if conn:
      stmt = DbtPy.prepare(conn, insert)
      
      if DbtPy.execute(stmt, (None, 'ghost', None, None)):
        stmt = DbtPy.exec_immediate(conn, select)
        row = DbtPy.fetch_tuple(stmt)
        while ( row ): 
          #row.each { |child| puts child }
          for child in row:
            print(child)
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
