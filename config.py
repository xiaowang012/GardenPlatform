#coding=utf-8
import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))


class DataBaseConfig(object):
    DEBUG = True
    #sqlite
    #SQLALCHEMY_DATABASE_URI =   "sqlite:///"+os.path.join(os.sep,basedir + os.sep +"database", "database123.db")
    #mysql
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/gardenplatform?charset=utf8"
	# SQLALCHEMY_TRACK_MODIFICATIONS = True


class EmailConfig(object):
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USERNAME = '1300202481@qq.com'
    MAIL_PASSWORD = 'univlugrxnlbhcdd'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True



class Config:
    SECRET_KEY = 'r34r3ewfwfffffffffffffffffffff'
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
