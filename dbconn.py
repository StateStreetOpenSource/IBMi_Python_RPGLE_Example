'''
----------------------------------------------------------------------------------------------------
 Copyright (c) 2019 StateStreetOpenSource
 All rights reserved.

 Program Name: dbconn.py
 Program Description: Establish a database connection to DB2 on IBM i from a remote Linux box 
                      or locally from the IBM i.

 Redistribution of this code, with or without modification, is permitted providing the following
 conditions are met.
   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimers.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR THE AUTHOR'S EMPLOYER BE
 LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION),
 HOWEVER CAUSED (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 Usage...
 c1, conn = db2conn()
 sqlstr = "select some_field from some.file"
 c1.execute(sqlstr)
 for row in c1.fetchall():
     myField = row[0]
 conn.close()  
----------------------------------------------------------------------------------------------------
'''

try:
    import ibm_db
    import ibm_db_dbi
    conType = 'LOCAL'
except:
    try:
        import pyodbc
        conType = 'REMOTE'
    except:
        conType = 'UNDEFINED'

def db2conn():
    try:
        if conType == 'LOCAL':
            conn = ibm_db_dbi.connect('DATABASE=*LOCAL')
            
        elif conType == 'REMOTE':
            conn = pyodbc.connect(
            DRIVER='IBM i Access ODBC Driver',
            SYSTEM='your IBMi IP',
            UID='IBM I USERNAME',
            PWD='IBM I PASSWORD')
            
        else:
            return None, None
        c1 = conn.cursor()
        return c1, conn 

    except:
        if conType == 'LOCAL':
            print("Connection Error:", ibm_db.conn_errormsg())
        else:
            print("Connection Error:", conn.conn_errormsg())
        return None, None