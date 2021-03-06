#coding=utf-8
import os
import json
basedir = os.path.abspath(os.path.dirname(__file__))

#get Parameters
para_path = basedir +os.sep + "parameters.json"
try:
    with open(para_path) as f:
        paras = json.load(f)       
except:
    raise Exception("read json config error!")
    
class Config:
    #secret_key
    SECRET_KEY = paras['SECRET_KEY']
    #mysql
    SQLALCHEMY_DATABASE_URI = paras["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    #email
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USERNAME = paras["MAIL_USERNAME"]
    MAIL_PASSWORD = paras["MAIL_PASSWORD"]
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

