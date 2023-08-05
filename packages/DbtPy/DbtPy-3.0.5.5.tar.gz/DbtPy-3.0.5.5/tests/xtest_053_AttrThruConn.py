#

#

#

import unittest, sys
import DbtPy
import config
from testfunctions import DbtPyTestFunctions

class DbtPyTestCase(unittest.TestCase):

  def test_053_AttrThruConn(self):
    obj = DbtPyTestFunctions()
    obj.assert_expect(self.run_test_053)

  def run_test_053(self):
    print("Client attributes passed through conection string:")

    options1 = {DbtPy.SQL_ATTR_INFO_USERID: 'db2inst1'}
    conn1 = DbtPy.connect(config.ConnStr, config.user, config.password, options1)
    val = DbtPy.get_option(conn1, DbtPy.SQL_ATTR_INFO_USERID, 1)
    print(val)

    options2 = {DbtPy.SQL_ATTR_INFO_ACCTSTR: 'account'}
    conn2 = DbtPy.connect(config.ConnStr, config.user, config.password, options2)
    val = DbtPy.get_option(conn2, DbtPy.SQL_ATTR_INFO_ACCTSTR, 1)
    print(val)

    options3 = {DbtPy.SQL_ATTR_INFO_APPLNAME: 'myapp'}
    conn3 = DbtPy.connect(config.ConnStr, config.user, config.password, options3)
    val = DbtPy.get_option(conn3, DbtPy.SQL_ATTR_INFO_APPLNAME, 1)
    print(val)

    options4 = {DbtPy.SQL_ATTR_INFO_WRKSTNNAME: 'workstation'}
    conn4 = DbtPy.connect(config.ConnStr, config.user, config.password, options4)
    val = DbtPy.get_option(conn4, DbtPy.SQL_ATTR_INFO_WRKSTNNAME, 1)
    print(val)

    options5 = {DbtPy.SQL_ATTR_INFO_USERID: 'kfb',
                DbtPy.SQL_ATTR_INFO_WRKSTNNAME: 'kfbwork',
                DbtPy.SQL_ATTR_INFO_ACCTSTR: 'kfbacc',
                DbtPy.SQL_ATTR_INFO_APPLNAME: 'kfbapp'}
    conn5 = DbtPy.connect(config.ConnStr, config.user, config.password, options5)
    val = DbtPy.get_option(conn5, DbtPy.SQL_ATTR_INFO_USERID, 1)
    print(val)
    val = DbtPy.get_option(conn5, DbtPy.SQL_ATTR_INFO_ACCTSTR, 1)
    print(val)
    val = DbtPy.get_option(conn5, DbtPy.SQL_ATTR_INFO_APPLNAME, 1)
    print(val)
    val = DbtPy.get_option(conn5, DbtPy.SQL_ATTR_INFO_WRKSTNNAME, 1)
    print(val)

    print("Client attributes passed post-conection:")

    options5 = {DbtPy.SQL_ATTR_INFO_USERID: 'db2inst1'}
    conn5 = DbtPy.connect(config.ConnStr, config.user, config.password)
    rc = DbtPy.set_option(conn5, options5, 1)
    val = DbtPy.get_option(conn5, DbtPy.SQL_ATTR_INFO_USERID, 1)
    print(val)

    options6 = {DbtPy.SQL_ATTR_INFO_ACCTSTR: 'account'}
    conn6 = DbtPy.connect(config.ConnStr, config.user, config.password)
    rc = DbtPy.set_option(conn6, options6, 1)
    val = DbtPy.get_option(conn6, DbtPy.SQL_ATTR_INFO_ACCTSTR, 1)
    print(val)

    options7 = {DbtPy.SQL_ATTR_INFO_APPLNAME: 'myapp'}
    conn7 = DbtPy.connect(config.ConnStr, config.user, config.password)
    rc = DbtPy.set_option(conn7, options7, 1)
    val = DbtPy.get_option(conn7, DbtPy.SQL_ATTR_INFO_APPLNAME, 1)
    print(val)

    options8 = {DbtPy.SQL_ATTR_INFO_WRKSTNNAME: 'workstation'}
    conn8 = DbtPy.connect(config.ConnStr, config.user, config.password)
    rc = DbtPy.set_option(conn8, options8, 1)
    val = DbtPy.get_option(conn8, DbtPy.SQL_ATTR_INFO_WRKSTNNAME, 1)
    print(val)

#__END__
#__LUW_EXPECTED__
#Client attributes passed through conection string:
#db2inst1
#account
#myapp
#workstation
#kfb
#kfbacc
#kfbapp
#kfbwork
#Client attributes passed post-conection:
#db2inst1
#account
#myapp
#workstation
#__ZOS_EXPECTED__
#Client attributes passed through conection string:
#db2inst1
#account
#myapp
#workstation
#kfb
#kfbacc
#kfbapp
#kfbwork
#Client attributes passed post-conection:
#db2inst1
#account
#myapp
#workstation
#__SYSTEMI_EXPECTED__
#Client attributes passed through conection string:
#db2inst1
#account
#myapp
#workstation
#kfb
#kfbacc
#kfbapp
#kfbwork
#Client attributes passed post-conection:
#db2inst1
#account
#myapp
#workstation
#__IDS_EXPECTED__
#Client attributes passed through conection string:
#db2inst1
#account
#myapp
#workstation
#kfb
#kfbacc
#kfbapp
#kfbwork
#Client attributes passed post-conection:
#db2inst1
#account
#myapp
#workstation
