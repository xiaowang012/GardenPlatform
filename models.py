#coding=utf-8
from dbs import db

#定义数据表和字段
class Books(db.Model):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    book_name = db.Column(db.String(50))
    book_type = db.Column(db.String(50))
    book_introduction = db.Column(db.String(100))
    issue_year = db.Column(db.String(50))
    book_file_name = db.Column(db.String(50))
    add_book_time = db.Column(db.String(50))
    number_of_downloads = db.Column(db.Integer)

    def __init__(self,id,book_name,book_type,book_introduction,issue_year,book_file_name,add_book_time,number_of_downloads):
        self.id = id
        self.book_name = book_name
        self.book_type = book_type
        self.book_introduction = book_introduction
        self.issue_year = issue_year
        self.book_file_name = book_file_name
        self.add_book_time = add_book_time
        self.number_of_downloads = number_of_downloads
        
#用户表
class User(db.Model):
    username = db.Column(db.String(50),primary_key = True)
    hash_pwd = db.Column(db.String(100))
    salt = db.Column(db.String(100))
    group_id = db.Column(db.Integer)
    add_time = db.Column(db.String(50))

    def __init__(self,username,hash_pwd,salt,group_id,add_time):
        self.username = username
        self.hash_pwd = hash_pwd
        self.salt = salt
        self.group_id =group_id
        self.add_time = add_time

#权限表
class Permission(db.Model):
    id = db.Column(db.Integer,autoincrement=True,primary_key = True)
    name = db.Column(db.String(50))
    url = db.Column(db.String(50))
    description = db.Column(db.String(100))
    def __init__(self,id,name,url,description):
        self.id = id
        self.name = name
        self.url = url
        self.description = description
        
#用户组表      
class UserGroup(db.Model):
    id = db.Column(db.Integer(),autoincrement=True,primary_key = True)
    name = db.Column(db.String(50))

    def __init__(self,id,name):
        self.id = id
        self.name = name

