# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_133_ExecuteLongInputParams(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_133)

  def run_test_133(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)

    if (not conn):
      print("Connection failed.")
      return 0

    DbtPy.autocommit(conn, DbtPy.SQL_AUTOCOMMIT_OFF)

    print("Starting test ...")
    res = ''
    sql =  "INSERT INTO animals (id, breed, name, weight) VALUES (?, ?, ?, ?)"
    try:
      stmt = DbtPy.prepare(conn, sql)
      res = DbtPy.execute(stmt,(128, 'hacker of human and technological nature', 'Wez the ruler of all things PECL', 88.3))
      
      stmt = DbtPy.prepare(conn, "SELECT breed, name FROM animals WHERE id = ?")
      res = DbtPy.execute(stmt, (128,))
      row = DbtPy.fetch_assoc(stmt)
      
      for i in row:
	         print(i)

      DbtPy.rollback(conn)
      print("Done")
    except:
      print("SQLSTATE: %s" % DbtPy.stmt_error(stmt))
      print("Message: %s" % DbtPy.stmt_errormsg(stmt))

    try:
        stmt = DbtPy.prepare(conn, "SELECT breed, name FROM animals WHERE id = ?")
        res = DbtPy.execute(stmt, (128,))
        row = DbtPy.fetch_assoc(stmt)
        if (row):
            for i in row:
                print(i)
        print(res)
        print("SQLSTATE: %s" % DbtPy.stmt_error(stmt))
        print("Message: %s" % DbtPy.stmt_errormsg(stmt))
    except:
        print("An Exception is not expected")
        print("SQLSTATE: %s" % DbtPy.stmt_error(stmt))
        print("Message: %s" % DbtPy.stmt_errormsg(stmt))

    DbtPy.rollback(conn)
    print("Done")

#__END__
#__IDS_EXPECTED__
#Starting test ...
#
#SQLSTATE: 22001
#Message: [GBasedbt][GBase ODBC Driver]String data right truncation. SQLCODE=-11023
#True
#SQLSTATE: 
#Message: 
#Done
