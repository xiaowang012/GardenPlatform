#coding=utf-8
from flask import Flask,render_template,request,\
    url_for,redirect,session,Response,g,jsonify,abort
from forms import UserForms,RegisterForms,SearchPlantForms
from werkzeug.utils import secure_filename
from config import DataBaseConfig,Config
from models import User,Devices ,Permission,UserGroup
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

#跳转到主页或登录页
@app.route('/',methods = ['POST','GET'])
def host():
    if 'user_id' in session:
       return redirect('home')
    else:
        return redirect('login')

#用户注册
@app.route('/register',methods = ['POST','GET'])
def register():
    form = RegisterForms()
    if request.method == 'GET':
        return render_template('register.html',form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user=request.form['username']
            passw=request.form['password'] 
            if not User.query.filter_by(username = user).first():
                try:
                    username = user
                    salt = str(time.time())
                    hash_pwd = get_hash_value(passw,salt)
                    add_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    group_id = 2
                    data = User(username,hash_pwd,salt,group_id,add_time)
                    db.session.add(data)
                    db.session.commit()
                    message = 'Sign up: '+ user + ' SUCCESS!'
                    dic2 = {'title':'SUCCESS!','message':message,'frame_type':'alert alert-success alert-dismissable'}
                    return render_template('register.html',form = form,dic2 = dic2)
                except:
                    db.session.rollback()
                    message = 'Sign up: '+ user + ' ERROR!'
                    dic2 = {'title':'ERROR!','message':message,'frame_type':'alert alert-dismissable alert-danger'}
                    return render_template('register.html',form = form,dic2 = dic2)
                finally:
                    db.session.close()
                
            else:
                dic1 = {'title':'fail','message':'The user name already exists, please do not re-register!'}
                return render_template('register.html',form = form,dic1 = dic1)
        else:
            return render_template('register.html',form = form) 

#用户登录
@app.route('/login',methods = ['POST','GET'])
def login():
    if 'user_id' in session:
       return redirect('home')
    form = UserForms()
    if request.method == 'GET':
        return render_template('login.html',form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user=request.form['username']
            passw=request.form['password'] 
            res = User.query.filter(User.username == user).first()
            if res:
                #验证登录密码的哈希值是否和数据库中的密码哈希值相等
                new_pwd = get_hash_value(passw,res.salt)
                if new_pwd == res.hash_pwd:
                    #验证通过
                    session['user_id'] = user
                    return redirect(url_for('index'))
                else:
                    dic1 = {'title':'error','message':'Incorrect password or user does not exist!'}
                    return render_template('login.html',form = form,dic1 = dic1)
            else:
                dic1 = {'title':'error','message':'Incorrect password or user does not exist!'}
                return render_template('login.html',form =form,dic1 =dic1)
        else:
            return render_template('login.html',form = form)

#用户登出
@login_required
@app.route('/logout',methods = ['POST','GET'])
def logout():  
    if 'user_id' in session:
        session.pop('user_id')
    return redirect('login')

#用户主页
@login_required
#@routing_permission_check
@app.route('/home',methods = ['POST','GET'])
def index():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        return 'f'

#我的盆摘
@app.route('/my_plant',methods = ['POST','GET'])
def my_plant():
    form = SearchPlantForms()
    username = session.get('user_id')
    if request.method == 'GET':
        dic1 = {'username':username,'active1':'active','active2':'','active3':'',\
        'active4':'','active5':'','current_page_number':1}
        #查询devices表中的所有数据
        devices_info = Devices.query.limit(10).all()
        if len(devices_info) ==0:
            devices_info_list=[]
        else:
            devices_info_list = []
            for i in devices_info:
                devices_info_list.append(i.__dict__)
            style_list = ['success','info','warning','error']
            for dict_data in devices_info_list:
                style_value = random.choice(style_list)
                dict_data['style'] = style_value
        return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)
    elif request.method == 'POST':
        pass

#朋友圈
@app.route('/my_friends',methods = ['POST','GET'])
def my_friends():
    form = SearchBookForms()
    if request.method == 'GET':
        return render_template('my_friends.html',form = form)
    else:
        return 'f'

#后台管理
@app.route('/management',methods = ['POST','GET'])
def management():
    form = SearchBookForms()
    if request.method == 'GET':
        return render_template('management.html',form = form)
    else:
        return 'f'

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=5001,debug = True)
