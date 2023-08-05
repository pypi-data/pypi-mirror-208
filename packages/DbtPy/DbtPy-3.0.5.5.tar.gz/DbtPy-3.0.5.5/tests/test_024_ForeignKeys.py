# 

#

#
# NOTE: IDS requires that you pass the schema name (cannot pass None)

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_024_ForeignKeys(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_024)

  def run_test_024(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
    server = DbtPy.server_info( conn )
     
    if conn != 0:
      drop = 'DROP TABLE test_primary_keys'
      try:
        result = DbtPy.exec_immediate(conn, drop)
      except:
        pass
      drop = 'DROP TABLE test_keys'
      try:
        result = DbtPy.exec_immediate(conn, drop)
      except:
        pass
      drop = 'DROP TABLE test_foreign_keys'
      try:
        result = DbtPy.exec_immediate(conn, drop)
      except:
        pass

      statement = 'CREATE TABLE test_primary_keys (id INTEGER NOT NULL, PRIMARY KEY(id))'
      result = DbtPy.exec_immediate(conn, statement)
      statement = "INSERT INTO test_primary_keys VALUES (1)"
      result = DbtPy.exec_immediate(conn, statement)
      statement = 'CREATE TABLE test_keys (name VARCHAR(30) NOT NULL, idf INTEGER NOT NULL, FOREIGN KEY(idf) REFERENCES test_primary_keys(id), \
                   PRIMARY KEY(name))'
      result = DbtPy.exec_immediate(conn, statement)
      statement = "INSERT INTO test_keys VALUES ('vince', 1)"
      result = DbtPy.exec_immediate(conn, statement)
      statement = 'CREATE TABLE test_foreign_keys (namef VARCHAR(30) NOT NULL, id INTEGER NOT NULL, FOREIGN KEY(namef) REFERENCES test_keys(name))'
      result = DbtPy.exec_immediate(conn, statement)
      statement = "INSERT INTO test_foreign_keys VALUES ('vince', 1)"
      result = DbtPy.exec_immediate(conn, statement)

      stmt = DbtPy.foreign_keys(conn, None, config.user, 'test_primary_keys')
      
      row = DbtPy.fetch_tuple(stmt)
      print(row[2])
      print(row[3])
      print(row[6])
      print(row[7])

      stmt = DbtPy.foreign_keys(conn, None, None, None, None, config.user, 'test_keys')
      row = DbtPy.fetch_tuple(stmt)
      print(row[2])
      print(row[3])
      print(row[6])
      print(row[7])

      stmt = DbtPy.foreign_keys(conn, None, config.user, 'test_keys', None, None, None)
      row = DbtPy.fetch_tuple(stmt)
      print(row[2])
      print(row[3])
      print(row[6])
      print(row[7])

      stmt = DbtPy.foreign_keys(conn, None, config.user, 'test_keys', None, config.user, 'test_foreign_keys')
      row = DbtPy.fetch_tuple(stmt)
      print(row[2])
      print(row[3])
      print(row[6])
      print(row[7])

      stmt = DbtPy.foreign_keys(conn, None, config.user, 'test_keys', None, 'dummy_schema')
      row = DbtPy.fetch_tuple(stmt)
      if(not row):
        print("No Data Found")
      else:
        print(row[2])
        print(row[3])
        print(row[6])
        print(row[7])
      DbtPy.close(conn)
    else:
      print(DbtPy.conn_errormsg())
      print("Connection failed\n")

#__END__
#__IDS_EXPECTED__
#test_primary_keys
#id
#test_keys
#idf
#test_primary_keys
#id
#test_keys
#idf
#test_keys
#name
#test_foreign_keys
#namef
#test_keys
#name
#test_foreign_keys
#namef
#test_keys
#name
#test_foreign_keys
#namef
