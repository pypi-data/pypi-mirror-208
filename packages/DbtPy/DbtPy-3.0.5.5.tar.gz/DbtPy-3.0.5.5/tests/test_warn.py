
import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):
    def test_warn(self):
        obj = DbtPyTestFunctions()
        obj.assert_expect(self.run_test_warn)

    def run_test_warn(self):
        conn = DbtPy.connect(config.ConnStr, config.user, config.password)
            
        if conn:

            drop = "DROP TABLE TEST1"
            try:
                result = DbtPy.exec_immediate(conn,drop)
            except:
                pass

            # Create the table test1

            create = "CREATE TABLE TEST1 (COL1 CHAR(5))"
            result = DbtPy.exec_immediate(conn, create)

            # Insert a string longer than 5 characters to force an error 
            # DbtPy.stmt_warn() API

            query = 'INSERT INTO TEST1 VALUES (?)'
            stmt = DbtPy.prepare(conn, query)
            try:
                DbtPy.execute(stmt, ('ABCDEF',))
            except:
                pass
				
            print((DbtPy.stmt_warn(stmt)))
			
            DbtPy.close(conn)
        else:
            print ("Connection failed.")

#__END__
#__IDS_EXPECTED__
#[GBasedbt][GBase ODBC Driver]String data right truncation. SQLCODE=-11023
