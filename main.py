import cx_Oracle
##mode=cx_Oracle.SYSDBA
def dbconn( dbuser, dbpass, dbhost, dbname, dbport = '1521', sysdba = False ):
    tns = cx_Oracle.makedsn(dbhost,dbport,dbname)
    con = cx_Oracle.connect(dbuser,dbpass,tns)
    print tns
    return con;

def archivelog( conn ):
    cur = conn.cursor()
    cur.execute('select LOG_MODE from v$database')
    result = cur.fetchone()
    if result[0] == 'ARCHIVELOG':
        return True;
    else:
        return False;
# Test

db1_name = 'ORAP'
db1_host = '52.0.66.11'
db1_user = 'system'
db1_pass = 'Powerds01!'

db2_name = 'ORAS'
db2_host = '52.0.66.11'
db2_user = 'system'
db2_pass = 'Powerds01!'

print "Primary database is " + db1_name
print "Secondary database is " + db2_name

# Connects to primary DB
db1_conn = dbconn( dbuser=db1_user, dbpass=db1_pass, dbhost=db1_host, dbname=db1_name )

# Check if archivelog is enabled on first db
if not archivelog( db1_conn ):
    print 'Archiving is not enabled on Database ' + db1_name + '. Exiting...'
    db1_conn.close
    exit(1);


db1_cur = db1_conn.cursor()
db1_cur.execute('select * from v$archived_log')
for row in db1_cur:
    print row
# Check

print 'teste'
exit(0);
