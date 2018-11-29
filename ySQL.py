#!/usr/bin/python -tt
import sys
import cx_Oracle


# Send information to the database
def send_sql(sql, database):
    try:
        db = cx_Oracle.connect('OPERATIONS', 'OPERATIONS', database)
        cursor = db.cursor()
        cursor.execute(sql)

        # print 'Database rows effected:', cursor.rowcount
        db.commit()
        cursor.close()
        db.close()

    except cx_Oracle.DatabaseError, e:
        error, = e.args
        print >> sys.stderr, "Oracle-Error-Code:", error.code
        print >> sys.stderr, "Oracle-Error-Message:", error.message


# Returns only one item back to a variable
def get_sql_fetchone(sql, database):
    try:
        db = cx_Oracle.connect('OPERATIONS', 'OPERATIONS', database)
        cursor = db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return row[0]

        cursor.close()
        db.close()

    except cx_Oracle.DatabaseError, e:
        error, = e.args
        print >> sys.stderr, "Oracle-Error-Code:", error.code
        print >> sys.stderr, "Oracle-Error-Message:", error.message


# Returns a result set
def get_sql_fetchall(sql, database):
    try:
        db = cx_Oracle.connect('OPERATIONS', 'OPERATIONS', database)
        cursor = db.cursor()
        cursor.execute(sql)
        # columns = [i[0] for i in cursor.description]
        # results = [dict(zip(columns, row)) for row in cursor]
        results = cursor.fetchall()

        return results

        cursor.close()
        db.close()

    except cx_Oracle.DatabaseError, e:
        error, = e.args
        print >> sys.stderr, "Oracle-Error-Code:", error.code
        print >> sys.stderr, "Oracle-Error-Message:", error.message


# Returns column headers
def get_sql_column_headers(sql, database):
    try:
        db = cx_Oracle.connect('OPERATIONS', 'OPERATIONS', database)
        cursor = db.cursor()
        cursor.execute(sql)
        columns = [i[0] for i in cursor.description]
        # results = [dict(zip(columns, row)) for row in cursor]

        return columns

        cursor.close()
        db.close()

    except cx_Oracle.DatabaseError, e:
        error, = e.args
        print >> sys.stderr, "Oracle-Error-Code:", error.code
        print >> sys.stderr, "Oracle-Error-Message:", error.message