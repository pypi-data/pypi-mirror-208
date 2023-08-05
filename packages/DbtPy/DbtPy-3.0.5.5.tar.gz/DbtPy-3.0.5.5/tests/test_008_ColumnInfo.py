# 

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_008_ColumnInfo(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_008)

  def run_test_008(self):
    op = {DbtPy.ATTR_CASE: DbtPy.CASE_NATURAL}
    conn = DbtPy.connect(config.ConnStr, config.user, config.password, op)
    server = DbtPy.server_info( conn )
    result = DbtPy.columns(conn,None,None,"employee")
    row = DbtPy.fetch_both(result)
    value1 = None
    value2 = None
    value3 = None
    value4 = None
    if ('TABLE_NAME' in row):
      value1 = row['TABLE_NAME']
    if ('COLUMN_NAME' in row):
      value2 = row['COLUMN_NAME']
    if ('table_name' in row):
      value3 = row['table_name']
    if ('column_name' in row):
      value4 = row['column_name']
    print(value1)
    print(value2)
    print(value3)
    print(value4)

    op = {DbtPy.ATTR_CASE: DbtPy.CASE_UPPER}
    DbtPy.set_option(conn, op, 1)
    result = DbtPy.columns(conn,None,None,"employee")
    row = DbtPy.fetch_both(result)
    value1 = None
    value2 = None
    value3 = None
    value4 = None
    if ('TABLE_NAME' in row):
      value1 = row['TABLE_NAME']
    if ('COLUMN_NAME' in row):
      value2 = row['COLUMN_NAME']
    if ('table_name' in row):
      value3 = row['table_name']
    if ('column_name' in row):
      value4 = row['column_name']
    print(value1)
    print(value2)
    print(value3)
    print(value4)
    
    op = {DbtPy.ATTR_CASE: DbtPy.CASE_LOWER}
    DbtPy.set_option(conn, op, 1)
    result = DbtPy.columns(conn,None,None,"employee")
    row = DbtPy.fetch_both(result)
    value1 = None
    value2 = None
    value3 = None
    value4 = None
    if ('TABLE_NAME' in row):
      value1 = row['TABLE_NAME']
    if ('COLUMN_NAME' in row):
      value2 = row['COLUMN_NAME']
    if ('table_name' in row):
      value3 = row['table_name']
    if ('column_name' in row):
      value4 = row['column_name']
    print(value1)
    print(value2)
    print(value3)
    print(value4)

#__END__
#__IDS_EXPECTED__
#employee
#empno
#None
#None
#employee
#empno
#None
#None
#None
#None
#employee
#empno
