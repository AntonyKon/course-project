import mysql.connector
def dbconnect(dbname):
    try:
        mydb = mysql.connector.connect(user="root",
                                       password="",
                                       host="localhost",
                                       database=dbname
                                       )
    except:
        mydb = None
    return mydb