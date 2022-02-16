#coding=utf-8
from dbs import db

#设备表
class Devices(db.Model):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    user_name = db.Column(db.String(50))
    plant_name = db.Column(db.String(50))
    plant_type = db.Column(db.String(50))
    status = db.Column(db.String(100))
    last_watering_time = db.Column(db.String(50))
    suggest_watering_time = db.Column(db.String(50))
    device_name = db.Column(db.String(50))
    switch_number = db.Column(db.Integer)

    def __init__(self,id,user_name,plant_name,plant_type,status,last_watering_time,suggest_watering_time,device_name,switch_number):
        self.id = id
        self.user_name = user_name
        self.plant_name = plant_name
        self.plant_type = plant_type
        self.status = status
        self.last_watering_time = last_watering_time
        self.suggest_watering_time = suggest_watering_time
        self.device_name = device_name
        self.switch_number = switch_number
        
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

#指令表
# class Commands(db.Model):
#     pass
