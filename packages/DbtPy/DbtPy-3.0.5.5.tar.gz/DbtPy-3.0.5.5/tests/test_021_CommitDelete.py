# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_021_CommitDelete(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_021)

  def run_test_021(self):
    conn = DbtPy.connect(config.ConnStr, config.user, config.password)
      
    if conn:
      stmt = DbtPy.exec_immediate(conn, "SELECT count(*) FROM animals")
      res = DbtPy.fetch_tuple(stmt)
      rows = res[0]
      print(rows)
        
      DbtPy.autocommit(conn, 0)
      ac = DbtPy.autocommit(conn)
      if ac != 0:
        print("Cannot set DbtPy.AUTOCOMMIT_OFF\nCannot run test")
        #continue
        
      DbtPy.exec_immediate(conn, "DELETE FROM animals")
        
      stmt = DbtPy.exec_immediate(conn, "SELECT count(*) FROM animals")
      res = DbtPy.fetch_tuple(stmt)
      rows = res[0]
      print(rows)
        
      DbtPy.commit(conn)
      
      stmt = DbtPy.exec_immediate(conn, "SELECT count(*) FROM animals")
      res = DbtPy.fetch_tuple(stmt)
      rows = res[0]
      print(rows)

      # Populate the animal table
      animals = (
        (0, 'cat',        'Pook',         3.2),
        (1, 'dog',        'Peaches',      12.3),
        (2, 'horse',      'Smarty',       350.0),
        (3, 'gold fish',  'Bubbles',      0.1),
        (4, 'budgerigar', 'Gizmo',        0.2),
        (5, 'goat',       'Rickety Ride', 9.7),
        (6, 'llama',      'Sweater',      150)
      )
      insert = 'INSERT INTO animals (id, breed, name, weight) VALUES (?, ?, ?, ?)'
      stmt = DbtPy.prepare(conn, insert)
      if stmt:
        for animal in animals:
          result = DbtPy.execute(stmt, animal)
      DbtPy.commit(conn)
      DbtPy.close(conn)
    else:
      print("Connection failed.")
      
#__END__
#__LUW_EXPECTED__
#7
#0
#0
#__ZOS_EXPECTED__
#7
#0
#0
#__SYSTEMI_EXPECTED__
#7
#0
#0
#__IDS_EXPECTED__
#7
#0
#0
