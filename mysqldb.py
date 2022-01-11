import mysql.connector
import random

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="010804",
  database = "conversations"
)

mycur = mydb.cursor()

def get_videoss():
    a = ""
    mycur.execute("select * from video")
    for i in mycur.fetchall():
        a += i[0]
        a += ","
    return a

def insert_group(date, timestart, timeend, details, link):
    mycur.execute(f'insert into group_event value ("{details}", "{date}", "{timestart}", "{timeend}", "{link}")')
    mydb.commit()

def insert_one_c(date, timestart, details, added_by, members):
    mycur.execute(f'insert into one_nevent (event_date, start_time, event_details, added_by, members) value ("{date}", "{timestart}", "{details}", "{added_by}", "{members}")')
    mydb.commit()

def insert_one(date, timestart, details, added_by, members):
    mycur.execute(f'insert into one_event (event_date, start_time, event_details, added_by, members) value ("{date}", "{timestart}", "{details}", "{added_by}", "{members}")')
    mydb.commit()

def insert_app(info, added_by):
    mycur.execute(f'insert into one_approval (info, added_by) value ("{info}", "{added_by}")')
    mydb.commit()

def delete_column(index):
    mycur.execute(f'DELETE FROM one_nevent WHERE id="{index}"')
    mydb.commit()

def get_group():
    a = []
    mycur.execute("select * from group_event")
    for i in mycur.fetchall():
        if i not in a:
            i = list(i)
            i[2] += "-" + i[3]
            del i[3]
            i = tuple(i)
            a.append(i)
    return a


def get_none_teacher(username):
    a = []
    mycur.execute(f'select * from one_nevent where members = "{username}"')
    for i in mycur.fetchall():
        if i not in a:
            a.append(i)
    return a

def get_id_one():
    a = []
    mycur.execute(f'select * from one_nevent')
    for i in mycur.fetchall():
        if i not in a:
            a.append(i[0])
    return a

def get_nevent_id(x):
    a = []
    mycur.execute(f'SELECT * FROM one_nevent WHERE id="{x}"')
    for i in mycur.fetchall():
        if i not in a:
            a.append(i)
    return a

def get_added_by(username):
    a = []
    mycur.execute(f'SELECT * FROM one_approval WHERE added_by="{username}"')
    for i in mycur.fetchall():
        if i not in a:
            a.append(i[1])
    return a

def get_date_members(date, members):
    a = []
    mycur.execute(f'SELECT * FROM one_event WHERE event_date="{date}" and members="{members}"')
    for i in mycur.fetchall():
        if i not in a:
            a.append(i)
    return a

def get_addedby_members(added_by):
    mycur.execute(f'SELECT * FROM one_event WHERE added_by="{added_by}" or members="{added_by}"')
    a = []
    for i in mycur.fetchall():
        if i not in a:
            a.append(i)
    return a

def get_quote():
    mycur.execute("SELECT quote FROM quotes")
    list2 = mycur.fetchall()
    quot = random.choice(list2)
    return quot[0]

