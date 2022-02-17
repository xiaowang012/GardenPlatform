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

#全局变量
PLANT_NAME = []

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
                    dic1 = {'title':'error','message':'不正确的密码或用户不存在!'}
                    return render_template('login.html',form = form,dic1 = dic1)
            else:
                dic1 = {'title':'error','message':'不正确的密码或用户不存在!'}
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

#我的盆摘
@login_required
@app.route('/my_plant',methods = ['GET'])
def my_plant():
    form = SearchPlantForms()
    if request.method == 'GET':
        dic1 = {'active1':'active','active2':'','active3':'',\
        'active4':'','active5':'','current_page_number':1}
        #查询devices表中的所有数据
        devices_info_list=[]
        devices_info = Devices.query.limit(10).all()
        if len(devices_info) == 0:
            pass
        else:
            for i in devices_info:
                dic_search_info =  i.__dict__
                del dic_search_info['_sa_instance_state']
                devices_info_list.append(dic_search_info)
            style_list = ['success','info','warning','error']
            for dict_data in devices_info_list:
                dict_data['style'] = random.choice(style_list)
        return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的盆栽翻页
@login_required
@app.route('/my_plant/page')
def my_plant_page():
    form = SearchPlantForms()
    if request.method == 'GET':
        number = request.args.get('number')
        try:
            number = int(number)
        except:
            return abort(404)
        else:
            dic1 = {'active1':'','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':number}
            #根据页码控制分页样式
            if 1 <= number <= 5:
                dic1['active'+str(number)] = 'active'
            elif number > 5:
                dic1['active_next'] = 'active'
            #根据页码查询数据
            offset_num = (int(number)-1)*10
            limit_num = 10
            #查询devices表中的所有数据
            devices_info_list=[]
            devices_info = Devices.query.limit(limit_num).offset(offset_num).all()
            if len(devices_info) == 0:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)


#我的盆摘设备查询主页
@login_required
@app.route('/my_plant/search/page',methods = ['POST'])
def search_plant():
    form = SearchPlantForms()
    if request.method == 'POST':
        if form.validate_on_submit():
            plant_name = request.form['plant_name']
            PLANT_NAME.append(plant_name)
            #默认查询第一页(10条)的数据(直接post进来的数据存到PLANT_NAME中，翻页时用,点击翻页按钮为get请求)
            dic1 = {'active1':'active','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':1}
            #查询devices表中的所有数据
            devices_info_list=[]
            devices_info = Devices.query.filter_by(plant_name = plant_name).limit(10).all()
            if len(devices_info) == 0:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant1.html',form = form,dic1 = dic1,list1 = devices_info_list)
        else:
            form_err = form.errors['plant_name'][0]
            dic1 = {'active1':'active','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':1,'errors':form_err}
            #查询devices表中的所有数据
            devices_info_list=[]
            devices_info = Devices.query.limit(10).all()
            if len(devices_info) == 0:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant1.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的盆摘设备查询主页翻页
@login_required
@app.route('/my_plant/search/page',methods = ['GET'])
def search_plant_page():
    form = SearchPlantForms()
    if request.method == 'GET':
        number = request.args.get('number')
        try:
            number = int(number)
        except:
            return abort(404)
        else:
            dic1 = {'active1':'','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':number}
            #根据页码控制分页样式
            if 1 <= number <= 5:
                dic1['active'+str(number)] = 'active'
            elif number > 5:
                dic1['active_next'] = 'active'
            #根据页码查询数据
            offset_num = (int(number)-1)*10
            limit_num = 10
            #查询devices表中的所有数据
            if PLANT_NAME:
                plant_name = PLANT_NAME[-1]
                devices_info = Devices.query.filter_by(plant_name = PLANT_NAME[-1]).limit(limit_num).offset(offset_num).all()
            else:
                devices_info = []
            devices_info_list=[]
            if len(devices_info) == 0:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant1.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的设备按植物类别查询
@login_required
@app.route('/my_plant/search/type',methods = ['GET'])
def search_plant_page_type():
    form = SearchPlantForms()
    if request.method == 'GET':
        plant_type = request.args.get('type_1')
        number = request.args.get('number')
        if plant_type:
            try:
                number = int(number)
            except:
                return abort(404)
            else:
                dic1 = {'active1':'','active2':'','active3':'',\
                'active4':'','active5':'','current_page_number':number}
                #根据页码控制分页样式
                if 1 <= number <= 5:
                    dic1['active'+str(number)] = 'active'
                elif number > 5:
                    dic1['active_next'] = 'active'
                #根据页码查询数据
                offset_num = (int(number)-1)*10
                limit_num = 10
                #查询devices表中的所有数据
                devices_info = Devices.query.filter_by(plant_type = plant_type).limit(limit_num).offset(offset_num).all()
                devices_info_list=[]
                if len(devices_info) == 0:
                    pass
                else:
                    for i in devices_info:
                        dic_search_info =  i.__dict__
                        del dic_search_info['_sa_instance_state']
                        devices_info_list.append(dic_search_info)
                    style_list = ['success','info','warning','error']
                    for dict_data in devices_info_list:
                        dict_data['style'] = random.choice(style_list)
                return render_template('my_plant2.html',form = form,dic1 = dic1,list1 = devices_info_list)
        else:
            #没拿到类型参数
            return abort(404)

#朋友圈
@app.route('/my_friends',methods = ['POST','GET'])
def my_friends():
    form = SearchPlantForms()
    if request.method == 'GET':
        return render_template('my_friends.html',form = form)
    else:
        return 'f'

#后台管理
@app.route('/management',methods = ['POST','GET'])
def management():
    form = SearchPlantForms()
    if request.method == 'GET':
        return render_template('management.html',form = form)
    else:
        return 'f'

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=5001,debug = True)
