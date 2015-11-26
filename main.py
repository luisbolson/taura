import cx_Oracle, paramiko, os
##mode=cx_Oracle.SYSDBA

# Check is the connected database is in ARCHIVELOG mode
def dbinfo( conn ):
    cur = conn.cursor()
    cur.execute('select DBID,OPEN_MODE,LOG_MODE from v$database')
    result = cur.fetchone()
    return result;

def getSequence( conn ):
    cur = conn.cursor()
    result = cur.execute('SELECT max(sequence#) FROM v$log_history WHERE RESETLOGS_TIME = (select max(RESETLOGS_TIME) from v$log_history)')
    result = cur.fetchone()
    return result[0];

def sql ( conn, sql ):
    cur = conn.cursor()
    cur.execute( sql )
    result = cur.fetchall()
    return result;

def sqlFO ( conn, sql ):
    cur = conn.cursor()
    cur.execute( sql )
    result = cur.fetchone()
    return result;


# Variables
db1_name = 'ORAP'
db1_host = '52.0.66.11'
db1_port = '1521'
db1_user = 'sys'
db1_pass = 'Powerds01!'

db2_name = 'ORAP'
db2_host = '52.70.143.236'
db2_port = '1521'
db2_user = 'sys'
db2_pass = 'Powerds01!'

print "Primary database is " + db1_name
print "Secondary database is " + db2_name

db1_tns = cx_Oracle.makedsn(db1_host,db1_port,db1_name)
db1_conn = cx_Oracle.connect(db1_user,db1_pass,db1_tns,cx_Oracle.SYSDBA)

db2_tns = cx_Oracle.makedsn(db2_host,db2_port,db2_name)
db2_conn = cx_Oracle.connect(db2_user,db2_pass,db2_tns,cx_Oracle.SYSDBA)

db1_info = dbinfo(db1_conn)
db2_info = dbinfo(db2_conn)

db1_seq = getSequence( db1_conn )
db2_seq = getSequence( db2_conn )

db1_dbid = db1_info[0]
db1_open_mode = db1_info[1]
db1_log_mode = db1_info[2]

db2_dbid = db2_info[0]
db2_open_mode = db2_info[1]
db2_log_mode = db2_info[2]

db_diff = db1_seq - db2_seq
print "\nPrimary DB"
print "  DBID: ", db1_dbid
print "  Open Mode: " + db1_open_mode
print "  Log Mode: " + db1_log_mode
print "  Sequence: ", db1_seq
print "\nSecondary DB"
print "  DBID: ", db2_dbid
print "  Open: " + db2_open_mode
print "  Log Mode: " + db2_log_mode
print "  Sequence: ", db2_seq
print "\n"
print "Archive log lag is: ", db_diff

if db_diff == 0:
    print "Secondary DB is up to date. No actions needed. Exiting..."
    exit(0)

sql_loglist = 'select SEQUENCE#,NAME from v$archived_log where SEQUENCE# > ' + str(db2_seq)
log_list = sql( db1_conn , sql_loglist )

dir_list = []

for archive in log_list:
    dir_list.append(os.path.dirname(archive[1]))

dir_list_unique = set(dir_list)

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.connect(db2_host, username='ec2-user', key_filename='/Users/luis/lhb-win.pem')

for unique_dir in dir_list_unique:
    print unique_dir
    checkdircmd = '[ -d '+ unique_dir +' ] && echo OK'
    print checkdircmd
    stdin, stdout, stderr = ssh.exec_command("sudo su oracle -c '"+checkdircmd+"'",get_pty=True)
    cmdrtn = stdout.readline().rstrip()
    if cmdrtn != 'OK':
        print 'Directory does not exist'
        createdircmd = "sudo su oracle -c 'mkdir -p "+ unique_dir+"'"
        print createdircmd
        stdin, stdout, stderr = ssh.exec_command(createdircmd,get_pty=True)
        print stderr.readline()
    else:
        print 'Directory already exists'
#    print str(archive[0])+" "+ os.path.basename(archive[1])



exit(0)
