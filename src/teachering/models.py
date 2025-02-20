from peewee import *
from datetime import datetime

db = SqliteDatabase("attendance.db")

class User(Model):
    email = CharField(unique=True)
    password_hash = CharField()
    role = CharField(choices=[("teacher", "teacher"), ("student", "student")])

    class Meta:
        database = db

class Attendance(Model):
    student = ForeignKeyField(User, backref="attendances")
    status = CharField(choices=[("pending", "pending"), ("approved", "approved"), ("rejected", "rejected")])
    timestamp = DateTimeField(default=datetime.now)
    
    class Meta:
        database = db

db.connect()
db.create_tables([User, Attendance])
