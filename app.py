#coding=utf-8
from flask import Flask,render_template,request,\
    url_for,redirect,session,Response,g,jsonify,abort
from forms import UserForms,RegisterForms,UploadFileForms,SearchBookForms,\
    AddBooksForms,AddPermissionForms,UploadPermissionForms
from werkzeug.utils import secure_filename
from config import DataBaseConfig,Config
from models import User,Books,Permission,UserGroup
from decorator import login_required, \
    routing_permission_check,get_hash_value
import os
import xlrd
import time
from dbs import db
import random
import zipfile

#初始化
app = Flask(__name__)
app.config.from_object(DataBaseConfig)
app.config.from_object(Config)
db.init_app(app)

#创建数据表
#db.create_all(app=app)

@app.route("/")
def func():
    form = {'1':2}
    return render_template('index.html',form = form)




if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=5001,debug = True)
