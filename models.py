#coding=utf-8
from dbs import db
import datetime

#设备表
class Devices(db.Model):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)
    user_name = db.Column(db.String(50))
    plant_name = db.Column(db.String(50))
    plant_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    last_watering_time = db.Column(db.String(50))
    suggest_watering_time = db.Column(db.String(50))
    device_name = db.Column(db.String(50))
    switch_number = db.Column(db.Integer)
    add_time = db.Column(db.String(50))

    def __init__(self,id,user_name,plant_name,plant_type,status,last_watering_time,suggest_watering_time,device_name,switch_number,add_time):
        self.id = id
        self.user_name = user_name
        self.plant_name = plant_name
        self.plant_type = plant_type
        self.status = status
        self.last_watering_time = last_watering_time
        self.suggest_watering_time = suggest_watering_time
        self.device_name = device_name
        self.switch_number = switch_number
        self.add_time = add_time
        
#用户表
class User(db.Model):
    username = db.Column(db.String(50),primary_key = True)
    chinese_name = db.Column(db.String(100))
    sex = db.Column(db.String(50))
    birthday = db.Column(db.String(50))
    email = db.Column(db.String(50))
    hash_pwd = db.Column(db.String(100))
    salt = db.Column(db.String(100))
    group_id = db.Column(db.Integer)
    add_time = db.Column(db.String(50))

    def __init__(self,username,chinese_name,sex,birthday,email,hash_pwd,salt,group_id,add_time):
        self.username = username
        self.hash_pwd = hash_pwd
        self.salt = salt
        self.group_id =group_id
        self.add_time = add_time
        self.chinese_name = chinese_name
        self.sex = sex
        self.birthday = birthday
        self.email = email

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

#朋友圈消息表
class FriendInfo(db.Model):
    id = db.Column(db.Integer(),autoincrement=True,primary_key = True)
    send_user = db.Column(db.String(50))
    time_format = db.Column(db.String(50))
    picture_path = db.Column(db.String(100))
    picture_path_html = db.Column(db.String(100))
    message_title = db.Column(db.String(100))
    message_content = db.Column(db.String(200))
    comments_number = db.Column(db.Integer)
    like_number = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)

    def __init__(self,id,send_user,time_format,picture_path,picture_path_html,message_title,messgae_content,comments_number,like_number,create_time):
        self.id = id
        self.send_user = send_user
        self.time_format = time_format
        self.picture_path = picture_path
        self.picture_path_html = picture_path_html
        self.message_title = message_title
        self.message_content = messgae_content
        self.comments_number = comments_number
        self.like_number = like_number
        self.create_time = create_time

#朋友圈的评论信息表
class FriendComments(db.Model):
    id = db.Column(db.Integer(),autoincrement=True,primary_key = True)
    friendinfo_id = db.Column(db.Integer)
    commenting_user = db.Column(db.String(50))
    commenting_message = db.Column(db.String(200))
    commenting_time = db.Column(db.DateTime)

    def __init__(self,id,friendinfo_id,commenting_user,commenting_message,commenting_time):
        self.id = id
        self.friendinfo_id = friendinfo_id
        self.commenting_user = commenting_user
        self.commenting_message = commenting_message
        self.commenting_time = commenting_time

#朋友圈的点赞信息表
class FriendLikes(db.Model):
    id = db.Column(db.Integer(),autoincrement=True,primary_key = True)
    friendinfo_id = db.Column(db.Integer)
    like_user = db.Column(db.String(50))
    like_time = db.Column(db.DateTime)

    def __init__(self,id,friendinfo_id,like_user,like_time):
        self.id = id
        self.friendinfo_id = friendinfo_id
        self.like_user = like_user
        self.like_time = like_time


