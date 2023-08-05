# 

#

#

from decimal import Decimal
import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):
	def test_decimal(self):
		obj = DbtPyTestFunctions()
		obj.assert_expect(self.run_test_decimal)
	
	def run_test_decimal(self):
		conn = DbtPy.connect(config.ConnStr, config.user, config.password)
		
		if conn:
			serverinfo = DbtPy.server_info( conn )
			
			drop = "DROP TABLE STOCKSHARE"
			try:
				result = DbtPy.exec_immediate(conn,drop)
			except:
				pass
			
			# Create the table stockprice
			create = "CREATE TABLE STOCKSHARE (id SMALLINT NOT NULL, company VARCHAR(30), stockshare DECIMAL(7, 2))"
			result = DbtPy.exec_immediate(conn, create)
			
			# Insert Directly
			insert = "INSERT INTO STOCKSHARE (id, company, stockshare) VALUES (10, 'Megadeth', 100.002)"
			result = DbtPy.exec_immediate(conn, insert)
			
			# Prepare and Insert in the stockprice table
			stockprice = (\
					(20, "Zaral", 102.205),\
					(30, "Megabyte", "98.65"),\
					(40, "Visarsoft", Decimal("123.34")),\
					(50, "Mailersoft", Decimal("134.222")),\
					(60, "Kaerci", Decimal("100.976"))\
					)
			insert = 'INSERT INTO STOCKSHARE (id, company, stockshare) VALUES (?,?,?)'
			stmt = DbtPy.prepare(conn,insert)
			if stmt:
				for company in stockprice:
					result = DbtPy.execute(stmt,company)
			
			id = 70
			company = 'Nirvana'
			stockshare = Decimal("100.1234")
			try:
				DbtPy.bind_param(stmt, 1, id)
				DbtPy.bind_param(stmt, 2, company)
				DbtPy.bind_param(stmt, 3, stockshare)
				error = DbtPy.execute(stmt);
			except:
				excp = sys.exc_info()
				# slot 1 contains error message
				print(excp[1])
			
			# Select the result from the table and
			query = 'SELECT * FROM STOCKSHARE ORDER BY id'
			if (serverinfo.DBMS_NAME[0:3] != 'Inf'):
				stmt = DbtPy.prepare(conn, query, {DbtPy.SQL_ATTR_CURSOR_TYPE: DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
			else:
				stmt = DbtPy.prepare(conn, query)
			DbtPy.execute(stmt)
			data = DbtPy.fetch_both( stmt )
			while ( data ):
				print("%s : %s : %s\n" % (data[0], data[1], data[2]))
				data = DbtPy.fetch_both( stmt )
			try:
				stmt = DbtPy.prepare(conn, query, {DbtPy.SQL_ATTR_CURSOR_TYPE:  DbtPy.SQL_CURSOR_KEYSET_DRIVEN})
				DbtPy.execute(stmt)
				rc = DbtPy.fetch_row(stmt, -1)
				print("Fetch Row -1:%s " %str(rc))
			except:
				print("Requested row number must be a positive value")
			DbtPy.close(conn)
		else:
			print("Connection failed.")

#__END__
#__LUW_EXPECTED__
#10 : Megadeth : 100.00
#20 : Zaral : 102.20
#30 : Megabyte : 98.65
#40 : Visarsoft : 123.34
#50 : Mailersoft : 134.22
#60 : Kaerci : 100.97
#70 : Nirvana : 100.12
#Requested row number must be a positive value
#__ZOS_EXPECTED__
#10 : Megadeth : 100.00
#20 : Zaral : 102.20
#30 : Megabyte : 98.65
#40 : Visarsoft : 123.34
#50 : Mailersoft : 134.22
#60 : Kaerci : 100.97
#70 : Nirvana : 100.12
#Requested row number must be a positive value
#__IDS_EXPECTED__
#10 : Megadeth : 100.00
#20 : Zaral : 102.21
#30 : Megabyte : 98.65
#40 : Visarsoft : 123.34
#50 : Mailersoft : 134.22
#60 : Kaerci : 100.98
#70 : Nirvana : 100.12
#Requested row number must be a positive value