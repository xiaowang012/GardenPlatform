#coding=utf-8
from mimetypes import init
from flask import Flask,render_template,request,Response,url_for,redirect,session,g,jsonify,abort,flash
from forms import UserForms,RegisterForms,SearchPlantForms,AddDeviceForms,ImportDevicesForms,\
    UpdateDevicesForms,UserUpdatePasswordForms,MyFriendsSendMessageForms,MyFriendAddCommentsForms
from werkzeug.utils import secure_filename
from config import Config
from models import User,Devices ,Permission,UserGroup,FriendInfo,FriendComments,FriendLikes
from decorator import login_required,routing_permission_check,get_hash_value,PERMISSION_DICT
import os
import time
import datetime
from dbs import db
import random
import xlrd
import json

#初始化
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

#创建数据表
db.create_all(app=app)

#全局变量植物名称
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
            chinese_name = request.form['chinese_name']
            sex = request.form['sex']
            birthday = request.form['birthday']
            email = request.form['email']
            if not User.query.filter_by(username = user).first():
                try:
                    salt = str(time.time())
                    hash_pwd = get_hash_value(passw,salt)
                    add_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    group_id = 2
                    data = User(username = user,chinese_name = chinese_name,sex = sex,birthday = str(birthday),\
                    email = email,hash_pwd = hash_pwd,salt = salt,group_id = group_id,add_time = add_time)
                    db.session.add(data)
                    db.session.commit()
                    message = '注册: '+ user + ' 成功!'
                    dic2 = {'title':'SUCCESS!','message':message,'frame_type':'alert alert-success alert-dismissable'}
                    return render_template('register.html',form = form,dic2 = dic2)
                except:
                    db.session.rollback()
                    message = '注册: '+ user + ' 错误!'
                    dic2 = {'title':'ERROR!','message':message,'frame_type':'alert alert-dismissable alert-danger'}
                    return render_template('register.html',form = form,dic2 = dic2)
                finally:
                    db.session.close()              
            else:
                dic1 = {'title':'fail','message':'这个用户已经存在! 请不要重复注册!'}
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
@app.route('/logout',methods = ['POST','GET'])
@login_required
def logout():  
    if 'user_id' in session:
        session.pop('user_id')
    return redirect('login')

#用户主页
@app.route('/home',methods = ['POST','GET'])
@login_required
@routing_permission_check
def index():
    current_user = session.get('user_id')
    if request.method == 'GET':
        #定义dic1
        res = User.query.filter_by(username = current_user).first()
        if res:
            chinese_name = res.chinese_name
            sex = res.sex
            birthday = res.birthday
            email = res.email
            group_id = res.group_id
            if sex == 'Male':
                sex = '男'
            elif sex == 'Female':
                sex = '女'

            if group_id == 1:
                per = '管理员'
            elif group_id == 2:
                per = '普通用户'
            #将数据加入到dic1
            dic1 = {'current_user':current_user,'chinese_name':chinese_name,'sex':sex,\
                'birthday':birthday,'email':email,'permission':per}
        return render_template('home.html',dic1 = dic1)

#用户查看个人信息页面
# @app.route('/UserProfile',methods = ['GET'])
# @login_required
# #@routing_permission_check
# def get_user_profile():
#     #定义dic1字典用于渲染html的数据准备
#     dic1 = {}
#     #在dic1中添加从session 中获取的user_id 字段
#     dic1['current_user'] = session.get('user_id')
#     if request.method == 'GET':
#         return render_template('user_profile.html',dic1 = dic1)

#用户修改密码
@app.route('/update_password',methods = ['POST','GET'])
@login_required
@routing_permission_check
def update_password():
    form = UserUpdatePasswordForms()
    current_user = session.get('user_id')
    #定义dic1 字典
    dic1 = {}
    #将用户加入dic1
    dic1['current_user'] = current_user
    if request.method == 'GET':
        return render_template('update_password.html',form = form,dic1 = dic1)
    elif request.method == 'POST':
        if form.validate_on_submit():
            username = request.form['username']
            old_password = request.form['old_password'] 
            new_password1 = request.form['new_password1']
            new_password2 = request.form['new_password2']
            if new_password1 == new_password2:
                #根据用户名查表
                res = User.query.filter_by(username = username).first()
                if res:
                    #获取原密码的hash值
                    old_hash_password = res.hash_pwd
                    old_salt = res.salt
                    #计算输入密码的hash值
                    new_hash_password = get_hash_value(old_password,old_salt)
                    if old_hash_password == new_hash_password:
                        #验证通过，将新密码的hash写入，写入新salt
                        try:
                            new_salt = str(time.time())
                            new_hash_pwd = get_hash_value(new_password1,new_salt)
                            #更新
                            res.hash_pwd = new_hash_pwd
                            res.salt = new_salt
                            db.session.commit()
                            message = '修改: '+ username + ' 的密码成功!'
                            dic2 = {'title':'成功!','message':message,'frame_type':'alert alert-success alert-dismissable'}
                            return render_template('update_password.html',form = form,dic1 = dic1,dic2 = dic2)
                        except:
                            db.session.rollback()
                            message = '修改: '+ username + ' 的密码失败!'
                            dic2 = {'title':'失败!','message':message,'frame_type':'alert alert-dismissable alert-danger'}
                            return render_template('update_password.html',form = form,dic1 = dic1,dic2 = dic2)
                        finally:
                            db.session.close()              
                    else:
                        #输入原密码错误
                        message = '输入原密码错误! 请重新输入!'
                        dic2 = {'title':'失败!','message':message,'frame_type':'alert alert-dismissable alert-danger'}
                        return render_template('update_password.html',form = form,dic1 = dic1,dic2 = dic2)
                else:
                    #用户不存在!
                    message = '用户: '+ username + ' 不存在!'
                    dic2 = {'title':'失败!','message':message,'frame_type':'alert alert-dismissable alert-danger'}
                    return render_template('update_password.html',form = form,dic1 = dic1,dic2 = dic2)
            else:
                #两次输入的密码不一致
                message = '两次输入的密码不一致! 请重新输入!'
                dic2 = {'title':'失败!','message':message,'frame_type':'alert alert-dismissable alert-danger'}
                return render_template('update_password.html',form = form,dic1 = dic1,dic2 = dic2)
        else:   
            #未通过表单校验
            err_dic = form.errors
            errs = ''
            for key,value in err_dic.items():
                errs += value[0] + '  '
            message = errs
            dic2 = {'title':'失败!','message':message,'frame_type':'alert alert-dismissable alert-danger'}
            return render_template('update_password.html',form = form,dic1 = dic1,dic2 = dic2)

#我的盆摘
@app.route('/my_plant',methods = ['GET'])
@login_required
@routing_permission_check
def my_plant():
    form = SearchPlantForms()
    current_user = session.get('user_id')
    if request.method == 'GET':
        #定义dic1
        res = User.query.filter_by(username = current_user).first()
        if res:
            chinese_name = res.chinese_name
            sex = res.sex
            birthday = res.birthday
            email = res.email
            group_id = res.group_id
            if sex == 'Male':
                sex = '男'
            elif sex == 'Female':
                sex = '女'    
            if group_id == 1:
                per = '管理员'
            elif group_id == 2:
                per = '普通用户'
            #将数据加入到dic1
        dic1 = {'active1':'active','active2':'','active3':'','active4':'',\
            'active5':'','current_page_number':1,'current_user':current_user,\
            'chinese_name':chinese_name,'sex':sex,'birthday':birthday,'email':email,'permission':per}
        #查询devices表中的所有数据
        devices_info_list=[]
        devices_info = Devices.query.filter_by(user_name = current_user).limit(10)
        if not devices_info:
            pass
        else:
            for i in devices_info:
                dic_search_info =  i.__dict__
                del dic_search_info['_sa_instance_state']
                #根据plant_type字段确定中文花名
                plant_type_string = dic_search_info['plant_type']
                #花名和数字对应
                dic_plants = {"1":"月季花",
                            "2":"玫瑰花",
                            "3":"栀子花",
                            "4":"太阳花",
                            "5":"牡丹花",
                            "6":"杜鹃花",
                            "7":"其他"
                            }
                #更新字典
                try:
                    dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                except:
                    dic_search_info['plant_type'] = None  
                devices_info_list.append(dic_search_info)
            style_list = ['success','info','warning','error']
            for dict_data in devices_info_list:
                dict_data['style'] = random.choice(style_list)
        return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的盆栽翻页
@app.route('/my_plant/page',methods = ['GET'])
@login_required
@routing_permission_check
def my_plant_page():
    current_user = session.get('user_id')
    form = SearchPlantForms()
    if request.method == 'GET':
        number = request.args.get('number')
        try:
            number = int(number)
        except:
            return abort(404)
        else:
            #定义dic1
            res = User.query.filter_by(username = current_user).first()
            if res:
                chinese_name = res.chinese_name
                sex = res.sex
                birthday = res.birthday
                email = res.email
                group_id = res.group_id
                if sex == 'Male':
                    sex = '男'
                elif sex == 'Female':
                    sex = '女' 
                if group_id == 1:
                    per = '管理员'
                elif group_id == 2:
                    per = '普通用户'
            dic1 = {'active1':'','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':number,\
            'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per}
            #根据页码控制分页样式
            if 1 <= number <= 5:
                dic1['active'+str(number)] = 'active'
            elif number > 5:
                dic1['active_next'] = 'active'
            #根据页码查询数据
            offset_num = (number-1)*10
            limit_num = 10
            #查询devices表中的所有数据
            devices_info_list=[]
            devices_info = Devices.query.filter_by(user_name = current_user).limit(limit_num).offset(offset_num)
            if not devices_info:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    #根据plant_type字段确定中文花名
                    plant_type_string = dic_search_info['plant_type']
                    #花名和数字对应
                    dic_plants = {"1":"月季花",
                                "2":"玫瑰花",
                                "3":"栀子花",
                                "4":"太阳花",
                                "5":"牡丹花",
                                "6":"杜鹃花",
                                "7":"其他"
                                }
                    #更新字典
                    try:
                        dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                    except:
                        dic_search_info['plant_type'] = None
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的盆摘设备查询主页
@app.route('/my_plant/search/page',methods = ['POST'])
@login_required
@routing_permission_check
def search_plant():
    form = SearchPlantForms()
    current_user = session.get('user_id')
    if request.method == 'POST':
        if form.validate_on_submit():
            plant_name = request.form['plant_name']
            PLANT_NAME.append(plant_name)
            #默认查询第一页(10条)的数据(直接post进来的数据存到PLANT_NAME中，翻页时用,点击翻页按钮为get请求)
            #定义dic1
            res = User.query.filter_by(username = current_user).first()
            if res:
                chinese_name = res.chinese_name
                sex = res.sex
                birthday = res.birthday
                email = res.email
                group_id = res.group_id
                if sex == 'Male':
                    sex = '男'
                elif sex == 'Female':
                    sex = '女' 
                if group_id == 1:
                    per = '管理员'
                elif group_id == 2:
                    per = '普通用户'
            dic1 = {'active1':'active','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':1,'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per}
            #查询devices表中的所有数据
            devices_info_list=[]
            devices_info = Devices.query.filter_by(plant_name = plant_name,user_name = current_user).limit(10)
            if not devices_info:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    #根据plant_type字段确定中文花名
                    plant_type_string = dic_search_info['plant_type']
                    #花名和数字对应
                    dic_plants = {"1":"月季花",
                                "2":"玫瑰花",
                                "3":"栀子花",
                                "4":"太阳花",
                                "5":"牡丹花",
                                "6":"杜鹃花",
                                "7":"其他"
                                }
                    #更新字典
                    try:
                        dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                    except:
                        dic_search_info['plant_type'] = None
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant1.html',form = form,dic1 = dic1,list1 = devices_info_list)
        else:
            form_err = form.errors['plant_name'][0]
            #定义dic1
            res = User.query.filter_by(username = current_user).first()
            if res:
                chinese_name = res.chinese_name
                sex = res.sex
                birthday = res.birthday
                email = res.email
                group_id = res.group_id
                if sex == 'Male':
                    sex = '男'
                elif sex == 'Female':
                    sex = '女' 
                if group_id == 1:
                    per = '管理员'
                elif group_id == 2:
                    per = '普通用户'
            dic1 = {'active1':'active','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':1,\
            'errors':form_err,'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per}
            #查询devices表中的所有数据
            devices_info_list=[]
            devices_info = Devices.query.filter_by(user_name = current_user).limit(10)
            if not devices_info:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    #根据plant_type字段确定中文花名
                    plant_type_string = dic_search_info['plant_type']
                    #花名和数字对应
                    dic_plants = {"1":"月季花",
                                "2":"玫瑰花",
                                "3":"栀子花",
                                "4":"太阳花",
                                "5":"牡丹花",
                                "6":"杜鹃花",
                                "7":"其他"
                                }
                    #更新字典
                    try:
                        dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                    except:
                        dic_search_info['plant_type'] = None
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant1.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的盆摘设备查询主页翻页
@app.route('/my_plant/search/page',methods = ['GET'])
@login_required
@routing_permission_check
def search_plant_page():
    form = SearchPlantForms()
    current_user = session.get('user_id')
    if request.method == 'GET':
        number = request.args.get('number')
        try:
            number = int(number)
        except:
            return abort(404)
        else:
            #定义dic1
            res = User.query.filter_by(username = current_user).first()
            if res:
                chinese_name = res.chinese_name
                sex = res.sex
                birthday = res.birthday
                email = res.email
                group_id = res.group_id
                if sex == 'Male':
                    sex = '男'
                elif sex == 'Female':
                    sex = '女' 
                if group_id == 1:
                    per = '管理员'
                elif group_id == 2:
                    per = '普通用户'
            dic1 = {'active1':'','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':number,\
            'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per}
            #根据页码控制分页样式
            if 1 <= number <= 5:
                dic1['active'+str(number)] = 'active'
            elif number > 5:
                dic1['active_next'] = 'active'
            #根据页码查询数据
            offset_num = (number-1)*10
            limit_num = 10
            #查询devices表中的所有数据
            if PLANT_NAME:
                plant_name = PLANT_NAME[-1]
                devices_info = Devices.query.filter_by(plant_name = PLANT_NAME[-1],user_name = current_user).limit(limit_num).offset(offset_num)
            else:
                devices_info = []
            devices_info_list=[]
            if not devices_info:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    #根据plant_type字段确定中文花名
                    plant_type_string = dic_search_info['plant_type']
                    #花名和数字对应
                    dic_plants = {"1":"月季花",
                                "2":"玫瑰花",
                                "3":"栀子花",
                                "4":"太阳花",
                                "5":"牡丹花",
                                "6":"杜鹃花",
                                "7":"其他"
                                }
                    #更新字典
                    try:
                        dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                    except:
                        dic_search_info['plant_type'] = None 
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant1.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的盆摘按植物类别查询
@app.route('/my_plant/search/type',methods = ['GET'])
@login_required
@routing_permission_check
def search_plant_page_type():
    form = SearchPlantForms()
    current_user = session.get('user_id')
    if request.method == 'GET':
        plant_type = request.args.get('plant_type')
        number = request.args.get('number')
        if plant_type:
            try:
                number = int(number)
            except:
                return abort(404)
            else:
                #定义dic1
                res = User.query.filter_by(username = current_user).first()
                if res:
                    chinese_name = res.chinese_name
                    sex = res.sex
                    birthday = res.birthday
                    email = res.email
                    group_id = res.group_id
                    if sex == 'Male':
                        sex = '男'
                    elif sex == 'Female':
                        sex = '女' 
                    if group_id == 1:
                        per = '管理员'
                    elif group_id == 2:
                        per = '普通用户'
                dic1 = {'active1':'','active2':'','active3':'',\
                'active4':'','active5':'','current_page_number':number,\
                'type1':plant_type,'current_user':current_user,'chinese_name':chinese_name,\
                'sex':sex,'birthday':birthday,'email':email,'permission':per}
                #根据页码控制分页样式
                if 1 <= number <= 5:
                    dic1['active'+str(number)] = 'active'
                elif number > 5:
                    dic1['active_next'] = 'active'
                #根据页码查询数据
                offset_num = (int(number)-1)*10
                limit_num = 10
                #查询devices表中的所有数据
                devices_info = Devices.query.filter_by(plant_type = plant_type,user_name = current_user).limit(limit_num).offset(offset_num)
                devices_info_list=[]
                if not devices_info:
                    pass
                else:
                    for i in devices_info:
                        dic_search_info =  i.__dict__
                        del dic_search_info['_sa_instance_state']
                        #根据plant_type字段确定中文花名
                        plant_type_string = dic_search_info['plant_type']
                        #花名和数字对应
                        dic_plants = {"1":"月季花",
                                    "2":"玫瑰花",
                                    "3":"栀子花",
                                    "4":"太阳花",
                                    "5":"牡丹花",
                                    "6":"杜鹃花",
                                    "7":"其他"
                                    }
                        #更新字典
                        try:
                            dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                        except:
                            dic_search_info['plant_type'] = None
                        devices_info_list.append(dic_search_info)
                    style_list = ['success','info','warning','error']
                    for dict_data in devices_info_list:
                        dict_data['style'] = random.choice(style_list)
                return render_template('my_plant2.html',form = form,dic1 = dic1,list1 = devices_info_list)
        else:
            #没拿到plant_type参数
            return abort(404)

#我的盆摘页面添加设备
@app.route('/my_plant/AddDevice',methods = ['POST'])
@login_required
@routing_permission_check
def add_devices():
    form = AddDeviceForms()
    current_user = session.get('user_id')
    if request.method == 'POST':
        if form.validate_on_submit():
            #写入数据库
            try:
                plant_name = request.form['plant_name']
                plant_type = request.form['plant_type']
                suggest_watering_time = request.form['suggest_watering_time']
                device_name = request.form['device_name']
                switch_number = request.form['switch_number']
                #添加到数据库
                db.session.add(Devices(id = None,user_name = current_user,plant_name = plant_name,plant_type = plant_type,\
                    status = None,last_watering_time = None,suggest_watering_time = suggest_watering_time,device_name = device_name,\
                        switch_number = switch_number,add_time = time.strftime('%Y-%m-%d %H:%M:%S')))
                db.session.commit()
                #渲染主页
                res = User.query.filter_by(username = current_user).first()
                if res:
                    chinese_name = res.chinese_name
                    sex = res.sex
                    birthday = res.birthday
                    email = res.email
                    group_id = res.group_id
                    if sex == 'Male':
                        sex = '男'
                    elif sex == 'Female':
                        sex = '女'    
                    if group_id == 1:
                        per = '管理员'
                    elif group_id == 2:
                        per = '普通用户'
                #将数据加入到dic1
                dic1 = {'active1':'active','active2':'','active3':'','active4':'',\
                'active5':'','current_page_number':1,'title':' 成功! ','message':'导入成功!',\
                'style':'alert alert-success alert-dismissable','current_user':current_user,\
                'chinese_name':chinese_name,'sex':sex,'birthday':birthday,'email':email,'permission':per}
                #查询devices表中的所有数据
                devices_info_list=[]
                devices_info = Devices.query.filter_by(user_name = current_user). limit(10)
                if not devices_info:
                    pass
                else:
                    for i in devices_info:
                        dic_search_info =  i.__dict__
                        del dic_search_info['_sa_instance_state']
                        #根据plant_type字段确定中文花名
                        plant_type_string = dic_search_info['plant_type']
                        #花名和数字对应
                        dic_plants = {"1":"月季花",
                                    "2":"玫瑰花",
                                    "3":"栀子花",
                                    "4":"太阳花",
                                    "5":"牡丹花",
                                    "6":"杜鹃花",
                                    "7":"其他"
                                    }
                        #更新字典
                        try:
                            dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                        except:
                            dic_search_info['plant_type'] = None  
                        devices_info_list.append(dic_search_info)
                    style_list = ['success','info','warning','error']
                    for dict_data in devices_info_list:
                        dict_data['style'] = random.choice(style_list)
                return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)
            except:
                db.session.rollback()
                #渲染主页
                res = User.query.filter_by(username = current_user).first()
                if res:
                    chinese_name = res.chinese_name
                    sex = res.sex
                    birthday = res.birthday
                    email = res.email
                    group_id = res.group_id
                    if sex == 'Male':
                        sex = '男'
                    elif sex == 'Female':
                        sex = '女'    
                    if group_id == 1:
                        per = '管理员'
                    elif group_id == 2:
                        per = '普通用户'
                dic1 = {'active1':'active','active2':'','active3':'',\
                'active4':'','active5':'','current_page_number':1,\
                'title':' 错误! ','message':'导入失败!','current_user':current_user,\
                'style':'alert alert-dismissable alert-danger','chinese_name':chinese_name,\
                    'sex':sex,'birthday':birthday,'email':email,'permission':per}
                #查询devices表中的所有数据
                devices_info_list=[]
                devices_info = Devices.query.filter_by(user_name = current_user). limit(10)
                if not devices_info:
                    pass
                else:
                    for i in devices_info:
                        dic_search_info =  i.__dict__
                        del dic_search_info['_sa_instance_state']
                        #根据plant_type字段确定中文花名
                        plant_type_string = dic_search_info['plant_type']
                        #花名和数字对应
                        dic_plants = {"1":"月季花",
                                    "2":"玫瑰花",
                                    "3":"栀子花",
                                    "4":"太阳花",
                                    "5":"牡丹花",
                                    "6":"杜鹃花",
                                    "7":"其他"
                                    }
                        #更新字典
                        try:
                            dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                        except:
                            dic_search_info['plant_type'] = None  
                        devices_info_list.append(dic_search_info)
                    style_list = ['success','info','warning','error']
                    for dict_data in devices_info_list:
                        dict_data['style'] = random.choice(style_list)
                return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)
            finally:
                db.session.close()
        else:
            #未通过表单校验，将错误消息拿出来
            err_dic = form.errors
            err1 = ''
            for key,value in err_dic.items():
                err1 += value[0] +'   '
            #渲染主页
            res = User.query.filter_by(username = current_user).first()
            if res:
                chinese_name = res.chinese_name
                sex = res.sex
                birthday = res.birthday
                email = res.email
                group_id = res.group_id
                if sex == 'Male':
                    sex = '男'
                elif sex == 'Female':
                    sex = '女'    
                if group_id == 1:
                    per = '管理员'
                elif group_id == 2:
                    per = '普通用户'
            dic1 = {'active1':'active','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':1,\
            'title':' 错误! ','message':err1,'current_user':current_user,\
            'style':'alert alert-dismissable alert-danger','chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per}
            #查询devices表中的所有数据
            devices_info_list=[]
            devices_info = Devices.query.filter_by(user_name = current_user).limit(10)
            if not devices_info:
                pass
            else:
                for i in devices_info:
                    dic_search_info =  i.__dict__
                    del dic_search_info['_sa_instance_state']
                    #根据plant_type字段确定中文花名
                    plant_type_string = dic_search_info['plant_type']
                    #花名和数字对应
                    dic_plants = {"1":"月季花",
                                "2":"玫瑰花",
                                "3":"栀子花",
                                "4":"太阳花",
                                "5":"牡丹花",
                                "6":"杜鹃花",
                                "7":"其他"
                                }
                    #更新字典
                    try:
                        dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                    except:
                        dic_search_info['plant_type'] = None  
                    devices_info_list.append(dic_search_info)
                style_list = ['success','info','warning','error']
                for dict_data in devices_info_list:
                    dict_data['style'] = random.choice(style_list)
            return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的盆摘页面修改设备
@app.route('/my_plant/UpdateDevices',methods = ['POST'])
@login_required
@routing_permission_check
def update_device():
    form = UpdateDevicesForms()
    current_user = session.get('user_id')
    if request.method == 'POST':
        if form.validate_on_submit():
            id1 = request.form['id1']
            plant_name1 = request.form['plant_name1']
            plant_type1 = request.form['plant_type1']
            suggest_watering_time1 = request.form['suggest_watering_time1']
            device_name1 = request.form['device_name1']
            switch_number1 = request.form['switch_number1']
            #print(id1,plant_name1,plant_type1,suggest_watering_time1,device_name1,switch_number1)
            if id !='':
                device_info = Devices.query.filter_by(id = int(id1)).first()
                if device_info:
                    try:
                        if device_info.plant_name != plant_name1:
                            device_info.plant_name = plant_name1
                            msg1 = 'plant_name'
                        else:
                            msg1 = ''

                        if device_info.plant_type != plant_type1:
                            device_info.plant_type = plant_type1
                            msg2 = 'plant_type'
                        else:
                            msg2 = ''

                        if device_info.suggest_watering_time != suggest_watering_time1:
                            device_info.suggest_watering_time = suggest_watering_time1
                            msg3 = 'suggest_watering_time'
                        else:
                            msg3 = ''

                        if device_info.device_name != device_name1:
                            device_info.device_name = device_name1
                            msg4 = 'device_name'
                        else:
                            msg4 = ''

                        if str(device_info.switch_number) != switch_number1:
                            #print(type(device_info.switch_number),type(switch_number1))
                            device_info.switch_number = switch_number1
                            msg5 = 'switch_number'
                        else:
                            msg5 = ''
                        db.session.commit()
                        #添加成功后渲染到主页
                        mssage_full = msg1 + ' '+msg2+ ' ' + msg3+ ' ' + msg4+ ' ' + msg5
                        message = '修改了 '+ mssage_full +  '字段,成功!'
                        style = 'alert alert-success alert-dismissable'
                        title = '成功! '
                    except:
                        db.session.rollback()
                        message = '写入数据库异常!'
                        style = 'alert alert-dismissable alert-danger'
                        title = '失败! ' 
                    finally:
                        db.session.close()
                else:
                    message = '数据库查询无数据!'
                    style = 'alert alert-dismissable alert-danger'
                    title = '错误! '   
            else:
                message = 'ID字段丢失!'
                style = 'alert alert-dismissable alert-danger'
                title = '错误! ' 
        else:
            err_dic = form.errors
            errs = ''
            for key,value in err_dic.items():
                errs += value[0] + ' '
            message = errs
            style = 'alert alert-dismissable alert-danger'
            title = 'forms错误! '
            print(errs)
        #返回对应的错误信息渲染页面
        res = User.query.filter_by(username = current_user).first()
        if res:
            chinese_name = res.chinese_name
            sex = res.sex
            birthday = res.birthday
            email = res.email
            group_id = res.group_id
            if sex == 'Male':
                sex = '男'
            elif sex == 'Female':
                sex = '女'    
            if group_id == 1:
                per = '管理员'
            elif group_id == 2:
                per = '普通用户'
            #将数据加入到dic1
        dic1 = {'active1':'active','active2':'','active3':'','active4':'',\
            'active5':'','current_page_number':1,'current_user':current_user,\
            'chinese_name':chinese_name,'sex':sex,'birthday':birthday,'email':email,'permission':per}
        #加入提示信息
        dic1['message'] = message
        dic1['style'] = style
        dic1['title'] = title
        #查询devices表中的所有数据
        devices_info_list=[]
        devices_info = Devices.query.filter_by(user_name = current_user).limit(10)
        if not devices_info:
            pass
        else:
            for i in devices_info:
                dic_search_info =  i.__dict__
                del dic_search_info['_sa_instance_state']
                #根据plant_type字段确定中文花名
                plant_type_string = dic_search_info['plant_type']
                #花名和数字对应
                dic_plants = {"1":"月季花",
                            "2":"玫瑰花",
                            "3":"栀子花",
                            "4":"太阳花",
                            "5":"牡丹花",
                            "6":"杜鹃花",
                            "7":"其他"
                            }
                #更新字典
                try:
                    dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                except:
                    dic_search_info['plant_type'] = None  
                devices_info_list.append(dic_search_info)
            style_list = ['success','info','warning','error']
            for dict_data in devices_info_list:
                dict_data['style'] = random.choice(style_list)
        return render_template('my_plant.html',form = form,list1 = devices_info_list,dic1 = dic1)

#我的盆摘页面删除设备
@app.route('/my_plant/DeleteDevice',methods = ['GET'])
@login_required
@routing_permission_check
def delete_device():
    id = request.args.get('id')
    try:
        id = int(id)
    except:
        return abort(404)
    else:
        search_devices = Devices.query.filter_by(id = id).first()
        if search_devices:
            if session.get('user_id') == search_devices.user_name:
                #删除
                db.session.delete(search_devices)
                db.session.commit()
                return redirect(url_for('my_plant'))
            else:
                return render_template('error_403.html')
        else:
            return '未查到数据!'

#我的盆摘页面浇花操作开始
@app.route('/my_plant/WateringOperation/start',methods = ['GET'])
@login_required
@routing_permission_check
def watering_operation_start():
    id1 = request.args.get('id')
    current_user = session.get('user_id')
    form = AddDeviceForms()
    if request.method == 'GET':
        if id1:
            device_info = Devices.query.filter_by(user_name = current_user,id = int(id1)).first()
            if device_info:
                #设备编号
                device_name = device_info.device_name
                switch_number = device_info.switch_number
                #print(device_name,str(switch_number))
                dic1 = {}
                dic1["device"] = device_name
                dic1["command"] = 'on#' + str(switch_number)
                time_1 = str(time.time())
                dic1["time"] = time_1
                json_path = os.getcwd()+ os.sep +"ControlServices" +os.sep + 'datas.json'
                txt_status_path = os.getcwd()+ os.sep +"ControlServices" +os.sep + 'logs.txt'
                with open(json_path,'w',encoding='utf-8') as f:
                    json.dump(dic1,f)
                status = None
                for i in range (10):
                    time.sleep(1)
                    with open(txt_status_path,'r',encoding='utf-8') as f:
                        text = f.read()
                    if time_1 in text:
                        status = 'OK'
                        break
                if status == 'OK':   
                    message = '设备: '+ str(id1) +' 浇水成功! '
                    style = 'alert alert-success alert-dismissable'
                    title = '成功!  ' 
                else:
                    message = '设备: '+ str(id1) +' 浇水失败! ' 
                    style = 'alert alert-dismissable alert-danger'
                    title = '失败!  '
            else:
                message = '设备权限错误! ' 
                style = 'alert alert-dismissable alert-danger'
                title = '失败!  '
        else:
            message = '设备不存在!' 
            style = 'alert alert-dismissable alert-danger'
            title = '失败!  '
    #渲染页面
    res = User.query.filter_by(username = current_user).first()
    if res:
        chinese_name = res.chinese_name
        sex = res.sex
        birthday = res.birthday
        email = res.email
        group_id = res.group_id
        if sex == 'Male':
            sex = '男'
        elif sex == 'Female':
            sex = '女'    
        if group_id == 1:
            per = '管理员'
        elif group_id == 2:
            per = '普通用户'
    dic1 = {'active1':'active','active2':'','active3':'','active4':'','active5':'','current_page_number':1,\
    'title':title,'message':message,'current_user':current_user,'style':style,'chinese_name':chinese_name,\
    'sex':sex,'birthday':birthday,'email':email,'permission':per}
    #查询devices表中的所有数据
    devices_info_list=[]
    devices_info = Devices.query.filter_by(user_name = current_user).limit(10)
    if not devices_info:
        pass
    else:
        for i in devices_info:
            dic_search_info =  i.__dict__
            del dic_search_info['_sa_instance_state']
            #根据plant_type字段确定中文花名
            plant_type_string = dic_search_info['plant_type']
            #花名和数字对应
            dic_plants = {"1":"月季花",
                        "2":"玫瑰花",
                        "3":"栀子花",
                        "4":"太阳花",
                        "5":"牡丹花",
                        "6":"杜鹃花",
                        "7":"其他"
                        }
            #更新字典
            try:
                dic_search_info['plant_type'] = dic_plants[plant_type_string] 
            except:
                dic_search_info['plant_type'] = None  
            devices_info_list.append(dic_search_info)
        style_list = ['success','info','warning','error']
        for dict_data in devices_info_list:
            dict_data['style'] = random.choice(style_list)
    return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)
    

#我的盆摘页面浇花操作停止
@app.route('/my_plant/WateringOperation/end',methods = ['GET'])
@login_required
@routing_permission_check
def watering_operation_stop():
    id2 = request.args.get('id')
    current_user = session.get('user_id')
    form = AddDeviceForms()
    if request.method == 'GET':
        if id2:
            device_info = Devices.query.filter_by(user_name = current_user,id = int(id2)).first()
            if device_info:
                #设备编号
                device_name = device_info.device_name
                switch_number = device_info.switch_number
                #print(device_name,str(switch_number))
                dic1 = {}
                dic1["device"] = device_name
                dic1["command"] = 'off#' + str(switch_number)
                time_1 = str(time.time())
                dic1["time"] = time_1
                json_path = os.getcwd()+ os.sep +"ControlServices" +os.sep + 'datas.json'
                txt_status_path = os.getcwd()+ os.sep +"ControlServices" +os.sep + 'logs.txt'
                with open(json_path,'w',encoding='utf-8') as f:
                    json.dump(dic1,f)
                status = None
                for i in range (10):
                    time.sleep(1)
                    with open(txt_status_path,'r',encoding='utf-8') as f:
                        text = f.read()
                    if time_1 in text:
                        status = 'OK'
                        break
                if status == 'OK':   
                    message = '设备: '+ str(id2) +' 停止成功! '
                    style = 'alert alert-success alert-dismissable'
                    title = '成功!  ' 
                else:
                    message = '设备: '+ str(id2) +' 停止失败! ' 
                    style = 'alert alert-dismissable alert-danger'
                    title = '失败!  '
            else:
                message = '设备权限错误! ' 
                style = 'alert alert-dismissable alert-danger'
                title = '失败!  '
        else:
            message = '设备不存在!' 
            style = 'alert alert-dismissable alert-danger'
            title = '失败!  '
    #渲染页面
    res = User.query.filter_by(username = current_user).first()
    if res:
        chinese_name = res.chinese_name
        sex = res.sex
        birthday = res.birthday
        email = res.email
        group_id = res.group_id
        if sex == 'Male':
            sex = '男'
        elif sex == 'Female':
            sex = '女'    
        if group_id == 1:
            per = '管理员'
        elif group_id == 2:
            per = '普通用户'
    dic1 = {'active1':'active','active2':'','active3':'','active4':'','active5':'','current_page_number':1,\
    'title':title,'message':message,'current_user':current_user,'style':style,'chinese_name':chinese_name,\
    'sex':sex,'birthday':birthday,'email':email,'permission':per}
    #查询devices表中的所有数据
    devices_info_list=[]
    devices_info = Devices.query.filter_by(user_name = current_user).limit(10)
    if not devices_info:
        pass
    else:
        for i in devices_info:
            dic_search_info =  i.__dict__
            del dic_search_info['_sa_instance_state']
            #根据plant_type字段确定中文花名
            plant_type_string = dic_search_info['plant_type']
            #花名和数字对应
            dic_plants = {"1":"月季花",
                        "2":"玫瑰花",
                        "3":"栀子花",
                        "4":"太阳花",
                        "5":"牡丹花",
                        "6":"杜鹃花",
                        "7":"其他"
                        }
            #更新字典
            try:
                dic_search_info['plant_type'] = dic_plants[plant_type_string] 
            except:
                dic_search_info['plant_type'] = None  
            devices_info_list.append(dic_search_info)
        style_list = ['success','info','warning','error']
        for dict_data in devices_info_list:
            dict_data['style'] = random.choice(style_list)
    return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)
    

#我的盆摘页面浇花操作定时浇花
@app.route('/my_plant/AutoWatering',methods = ['GET'])
@login_required
@routing_permission_check
def auto_watering():
    pass

#我的盆摘页面批量导入设备
@app.route('/my_plant/ImportDevices',methods = ['POST','GET'])
@login_required
@routing_permission_check
def import_devices():
    form = ImportDevicesForms()
    current_user = session.get('user_id')
    if request.method =='POST':
        if form.validate_on_submit():
            #通过表单验证,接收文件并临时保存
            f = request.files['file']
            file_name = str(time.time())+f.filename
            file_path = os.getcwd() + os.path.join(os.sep,'Temp',file_name).replace(file_name,'')
            f.save(file_path + secure_filename(file_name))
            #打开文件
            if '.xlsx'  in file_name or '.xls' in file_name :
                #验证excel表头数据
                table_head = ['植物名称','植物类别','浇水周期','绑定设备','开关编号']
                work_book = xlrd.open_workbook(file_path + file_name)
                ws = work_book.sheet_by_name('Sheet1')
                if ws.row_values(0) == table_head:
                    add_data_list = []
                    for row in range(1,ws.nrows):
                        plant_name = ws.cell_value(row,0)
                        plant_type = ws.cell_value(row,1)
                        suggest_watering_time = ws.cell_value(row,2)
                        device_name = ws.cell_value(row,3)
                        switch_number = ws.cell_value(row,4)
                        #对plant_name进行处理，excel中为月季花/玫瑰花等，映射为数字类型
                        plants_number_dic = {"月季花":"1",
                                "玫瑰花":"2",
                                "栀子花":"3",
                                "太阳花":"4",
                                "牡丹花":"5",
                                "杜鹃花":"6",
                                "其他":"7"
                            }
                        try:
                            plant_type = plants_number_dic[plant_type]
                        except:
                            plant_type = None   
                        #判断excel中是否有数字(处理实际数据为1读出来是1.0的问题)
                        ctype =ws.cell(row,4).ctype
                        if ctype == 2:
                            switch_number = str(switch_number).replace('.0','')
                        #print(plant_name,plant_type,suggest_watering_time,device_name,switch_number)
                        #写入数据库
                        add_data_list.append(Devices(id = None,user_name = current_user,plant_name = plant_name,plant_type = plant_type,\
                                            status = None,last_watering_time = None,suggest_watering_time = suggest_watering_time,\
                                            device_name = device_name,switch_number = switch_number,add_time = time.strftime('%Y-%m-%d %H:%M:%S')))
                    #一次添加所有数据add_all
                    if len(add_data_list) != 0:
                        try:
                            db.session.add_all(add_data_list)
                            db.session.commit()
                            message = '导入成功! '
                            style = 'alert alert-success alert-dismissable'
                            title = '成功!  ' 
                        except:
                            db.session.rollback()
                            message = '导入失败! '
                            style = 'alert alert-dismissable alert-danger'
                            title = '错误!  ' 
                        finally:
                            db.session.close()
                    else:
                        message = '导入失败! EXCEL表中无数据! '
                        style = 'alert alert-dismissable alert-danger'
                        title = '错误!  '  
                else:
                    message = '导入失败! EXCEL表数据格式错误! 请重新上传! '
                    style = 'alert alert-dismissable alert-danger'
                    title = '错误!  '
            else:
                message = '导入失败! 文件类型错误! 请重新上传! '
                style = 'alert alert-dismissable alert-danger'
                title = '错误!  '
        else:
            #未通过表单校验,将forms里面的错误取出
            err_form = form.errors
            errs_all = ''
            for key,value in err_form.items():
                errs_all += value[0] + '  '
            #设置提示信息
            message = errs_all
            style = 'alert alert-dismissable alert-danger'
            title = '错误!  '
        #渲染页面
        res = User.query.filter_by(username = current_user).first()
        if res:
            chinese_name = res.chinese_name
            sex = res.sex
            birthday = res.birthday
            email = res.email
            group_id = res.group_id
            if sex == 'Male':
                sex = '男'
            elif sex == 'Female':
                sex = '女' 
            if group_id == 1:
                per = '管理员'
            elif group_id == 2:
                per = '普通用户'
        dic1 = {'active1':'active','active2':'','active3':'','active4':'','active5':'',\
        'current_page_number':1,'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per}
        #将提示信息加入到dic1中
        dic1['message'] = message
        dic1['title'] = title
        dic1['style'] = style

        #查询devices表中的前10条数据
        devices_info_list=[]
        devices_info = Devices.query.limit(10).all()
        if len(devices_info) == 0:
            pass
        else:
            for i in devices_info:
                dic_search_info =  i.__dict__
                del dic_search_info['_sa_instance_state']
                #根据plant_type字段确定中文花名
                plant_type_string = dic_search_info['plant_type']
                #花名和数字对应
                dic_plants = {"1":"月季花",
                            "2":"玫瑰花",
                            "3":"栀子花",
                            "4":"太阳花",
                            "5":"牡丹花",
                            "6":"杜鹃花",
                            "7":"其他"
                            }
                #更新字典
                try:
                    dic_search_info['plant_type'] = dic_plants[plant_type_string] 
                except:
                    dic_search_info['plant_type'] = None  
                devices_info_list.append(dic_search_info)
            style_list = ['success','info','warning','error']
            for dict_data in devices_info_list:
                dict_data['style'] = random.choice(style_list)
        return render_template('my_plant.html',form = form,dic1 = dic1,list1 = devices_info_list)

#我的盆摘页面批量导入设备下载模板文件
@app.route("/my_plant/ImportDevices/DownloadTemplateFile",methods = ['GET'])
@login_required
@routing_permission_check
def download_import_devices_template():
    file_name = 'template_devices.zip'
    file_path = os.getcwd() + os.path.join(os.sep,'media',file_name )
    if os.path.isfile(file_path) == True:
        #打开指定文件准备传输
        #循环读取文件
        def sendfile(file_path):
            with open(file_path, 'rb') as targetfile:
                while True:
                    data = targetfile.read(20*1024*1024)
                    if not data:
                        break
                    yield data
        response = Response(sendfile(file_path), content_type='app/octet-stream')
        response.headers["Content-disposition"] = 'attachment; filename=%s' % file_name 
        return response
    else:  
        return render_template('error_404.html')

#刷新权限PERMISSION_DICT的值
@app.route("/management/refresh")
@login_required
@routing_permission_check
def refresh_permission():
    cur_url = request.args.get('cur_url')
    if cur_url:
        #更新权限表
        #print(cur_url)
        user_group_list = []
        user_group_data = UserGroup.query.all()
        if user_group_data:
            for i in user_group_data:
                user_group_list.append( i.name)
            for j in user_group_list:
                result2 = Permission.query.filter(Permission.name == j).all()
                set1 = set()
                if result2:
                    for k in result2:
                        set1.add(k.url)
                    PERMISSION_DICT[j] = set1
                    return redirect(cur_url)
                else:
                    return abort(404)
        else:
            return abort(404)
    else:
        return abort(404)

#朋友圈
@app.route('/my_friends',methods = ['POST','GET'])
@login_required
@routing_permission_check
def my_friends():
    form = MyFriendsSendMessageForms()
    current_user = session.get('user_id')
    if request.method == 'GET':
        #定义字典渲染页面
        #定义dic1
        res = User.query.filter_by(username = current_user).first()
        if res:
            chinese_name = res.chinese_name
            sex = res.sex
            birthday = res.birthday
            email = res.email
            group_id = res.group_id
            if sex == 'Male':
                sex = '男'
            elif sex == 'Female':
                sex = '女' 
            if group_id == 1:
                per = '管理员'
            elif group_id == 2:
                per = '普通用户'
        dic1 = {'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per,'page_number':1}
        #查询朋友动态信息
        friends_info = FriendInfo.query.order_by(FriendInfo.create_time.desc()).limit(3)
        friends_info_list = []
        for i in friends_info:
            data = i.__dict__
            #根据data中的id查询评论数据
            #评论信息ID
            comment_id = data['id']
            #print(comment_id)
            comments_info = FriendComments.query.filter_by(friendinfo_id = comment_id).order_by(FriendComments.commenting_time.desc()).limit(5)
            comments_list = []
            for j in comments_info:
                data_1 = j.__dict__
                #删除多余字段
                del data_1['_sa_instance_state']
                data_1['style'] = random.choice(['success','info','warning','error',''])
                comments_list.append(data_1)
            data['comments_list'] = comments_list
            #对data进行处理
            del data['_sa_instance_state']
            del data['picture_path']
            #处理时间time_format
            digital_week_dic = {'1':'星期一','2':'星期二','3':'星期三','4':'星期四','5':'星期五','6':'星期六','7':'星期日'}
            time_list = data['time_format'].split(',')
            data['week'] = digital_week_dic[ time_list[3]]
            data['date'] = time_list[0] +'年' +time_list[1] +'月' + time_list[2] +'日'
            friends_info_list.append(data)
        return render_template('blog_1.html',dic1 = dic1, form = form ,list1 = friends_info_list)

#发盆友圈动态
@app.route('/my_friends/send_message',methods = ['POST','GET'])
@login_required
@routing_permission_check
def my_friends_send_message():
    form = MyFriendsSendMessageForms()
    current_user = session.get('user_id')
    if request.method == 'POST':
        if form.validate_on_submit():
            message_title = request.form['message_title']
            message_content = request.form['message_content']
            #接收图片
            f = request.files['picture']
            #print(f)
            if f:
                file_name = str(time.time()) + os.path.splitext(f.filename)[-1]
                file_path = os.getcwd() + os.sep + 'static' + os.sep + 'imgs' +os.sep
                f.save(file_path + secure_filename(file_name))
                picture_path = '.' + os.sep + 'static' + os.sep + 'imgs' + os.sep + file_name
                picture_path_html = '/static/imgs/' + file_name
            else:
                picture_path = None
                picture_path_html = None
            #print(message_title,message_content,picture_path)
            try:
                #获取格式化时间，包括星期，用逗号分隔，用于前端的渲染,split
                time_format = time.strftime('%Y,%m,%d,%w')
                send_user = current_user
                #评论数
                comments_number = 0
                #点赞数
                like_number = 0
                db.session.add(FriendInfo(id = None,send_user = send_user ,\
                    time_format = time_format,picture_path = picture_path,\
                    message_title = message_title,messgae_content = message_content,\
                    comments_number = comments_number,picture_path_html = picture_path_html,\
                    like_number = like_number,create_time = datetime.datetime.now()))
                db.session.commit()
                message = '发送动态成功!刷新后查看'
                title = '成功!'
                style = 'alert alert-success alert-dismissable'
            except:
                db.session.rollback()
                message = '写入数据错误!'
                title = '错误!'
                style = 'alert alert-dismissable alert-danger'
            finally:
                db.session.close()
        else:
            #未通过表单校验
            err_dic = form.errors
            errs = ''
            for key,value in err_dic.items():
                errs += value[0] + '  '
            message = errs
            title = '错误!'
            style = 'alert alert-dismissable alert-danger'
        #渲染页面
        #查询用户个人信息
        res = User.query.filter_by(username = current_user).first()
        if res:
            chinese_name = res.chinese_name
            sex = res.sex
            birthday = res.birthday
            email = res.email
            group_id = res.group_id
            if sex == 'Male':
                sex = '男'
            elif sex == 'Female':
                sex = '女' 
            if group_id == 1:
                per = '管理员'
            elif group_id == 2:
                per = '普通用户'
        dic1 = {'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per,'page_number':1}
        #把对应的提示信息加入到dic1中
        dic1['message'] = message
        dic1['title'] = title
        dic1['style'] = style
        #查询朋友动态信息
        friends_info = FriendInfo.query.order_by(FriendInfo.create_time.desc()).limit(3)
        friends_info_list = []
        for i in friends_info:
            data = i.__dict__
            #评论信息ID
            comment_id = data['id']
            #print(comment_id)
            comments_info = FriendComments.query.filter_by(friendinfo_id = comment_id).order_by(FriendComments.commenting_time.desc()).limit(5)
            comments_list = []
            for j in comments_info:
                data_1 = j.__dict__
                #删除多余字段
                del data_1['_sa_instance_state']
                data_1['style'] = random.choice(['success','info','warning','error',''])
                comments_list.append(data_1)
            data['comments_list'] = comments_list
            #对data进行处理
            del data['_sa_instance_state']
            del data['picture_path']
            #处理时间time_format
            digital_week_dic = {'1':'星期一','2':'星期二','3':'星期三','4':'星期四','5':'星期五','6':'星期六','7':'星期日'}
            time_list = data['time_format'].split(',')
            data['week'] = digital_week_dic[ time_list[3]]
            data['date'] = time_list[0] +'年' +time_list[1] +'月' + time_list[2] +'日'
            friends_info_list.append(data)
        return render_template('blog_1.html',dic1 = dic1, form = form ,list1 = friends_info_list)
        
#删除朋友圈动态(用户界面,管理员和普通用户都只能删除自己发的)
@app.route('/my_friends/delete_message',methods = ['GET'])
@login_required
#@routing_permission_check
def delete_my_message():
    if request.method == 'GET':
        cur_user = session.get('user_id')
        cur_url = request.args.get('cur_url')
        id = request.args.get('id')
        if cur_url:
            try:
                id = int(id)
            except:
                return abort(404)
            else:
                #根据id查用户
                user_info = FriendInfo.query.filter_by(id = id).first()
                if user_info:
                    if user_info.send_user == cur_user:
                        #当前用户和发送用户一致，执行删除操作
                        #删除static中的图片
                        file_path_remove = user_info.picture_path
                        if file_path_remove:
                            if os.path.isfile(file_path_remove) == True:
                                os.remove(file_path_remove)
                        db.session.delete(user_info)
                        db.session.commit()
                        flash('删除成功!')
                        return redirect(cur_url)
                    else:
                        flash('无权限删除别人的动态!')
                        return redirect(cur_url)
                else:
                    flash('用户未找到!')
                    return redirect(cur_url)
        else:
            return abort(404)

#朋友圈动态翻页
@app.route('/my_friends/nextpage',methods = ['GET'])
@login_required
#@routing_permission_check
def my_friend_next_page():
    form = MyFriendsSendMessageForms()
    current_user = session.get('user_id')
    if request.method == 'GET':
        #定义字典渲染页面
        #定义dic1
        page_number = request.args.get('page')
        try:
            page_number = int(page_number)
        except:
            return abort(404)
        else:
            res = User.query.filter_by(username = current_user).first()
            if res:
                chinese_name = res.chinese_name
                sex = res.sex
                birthday = res.birthday
                email = res.email
                group_id = res.group_id
                if sex == 'Male':
                    sex = '男'
                elif sex == 'Female':
                    sex = '女' 
                if group_id == 1:
                    per = '管理员'
                elif group_id == 2:
                    per = '普通用户'
            dic1 = {'current_user':current_user,'chinese_name':chinese_name,\
                'sex':sex,'birthday':birthday,'email':email,'permission':per,'page_number':page_number}
            #查询朋友动态信息
            #根据页码查询不同的数据
            offset_num = (page_number-1)*3
            limit_num = 3
            friends_info = FriendInfo.query.order_by(FriendInfo.create_time.desc()).limit(limit_num).offset(offset_num)
            friends_info_list = []
            for i in friends_info:
                data = i.__dict__
                #评论信息ID
                comment_id = data['id']
                #print(comment_id)
                comments_info = FriendComments.query.filter_by(friendinfo_id = comment_id).order_by(FriendComments.commenting_time.desc()).limit(5)
                comments_list = []
                for j in comments_info:
                    data_1 = j.__dict__
                    #删除多余字段
                    del data_1['_sa_instance_state']
                    data_1['style'] = random.choice(['success','info','warning','error',''])
                    comments_list.append(data_1)
                data['comments_list'] = comments_list
                #对data进行处理
                del data['_sa_instance_state']
                del data['picture_path']
                #处理时间time_format
                digital_week_dic = {'1':'星期一','2':'星期二','3':'星期三','4':'星期四','5':'星期五','6':'星期六','7':'星期日'}
                time_list = data['time_format'].split(',')
                data['week'] = digital_week_dic[ time_list[3]]
                data['date'] = time_list[0] +'年' +time_list[1] +'月' + time_list[2] +'日'
                friends_info_list.append(data)
            return render_template('blog_1.html',dic1 = dic1, form = form ,list1 = friends_info_list)

#添加朋友圈动态评论
@app.route('/my_friends/send_message/add_comments',methods = ['POST'])
@login_required
#@routing_permission_check
def my_friend_commenting_message():
    current_user = session.get('user_id')
    form = MyFriendAddCommentsForms()
    if request.method == 'POST':
        if form.validate_on_submit():
            friendinfo_id = request.form['friendinfo_id']
            commenting_message = request.form['commenting_message']
            commenting_user = current_user
            commenting_time = datetime.datetime.now()
            try:
                db.session.add(FriendComments(id = None,friendinfo_id = friendinfo_id,\
                    commenting_user= commenting_user,commenting_message = commenting_message,\
                    commenting_time = commenting_time))
                #更新评论数
                friends_info = FriendInfo.query.filter_by(id = friendinfo_id).first()
                if friends_info:
                    old_comments = friends_info.comments_number
                    friends_info.comments_number = old_comments + 1
                db.session.commit()
                message = '评论成功! 刷新后查看'
                title = '成功! '
                style = 'alert alert-success alert-dismissable'
            except:
                db.session.rollback()
                message = '数据库错误!'
                title = '错误!'
                style = 'alert alert-dismissable alert-danger'
            finally:
                db.session.close()
        else:
            #未通过表单校验
            err_dic = form.errors
            errs = ''
            for key,value in err_dic.items():
                errs += value[0] + '  '
            message = errs
            title = '错误! '
            style = 'alert alert-dismissable alert-danger'
        #渲染页面
        #渲染页面
        #查询用户个人信息
        res = User.query.filter_by(username = current_user).first()
        if res:
            chinese_name = res.chinese_name
            sex = res.sex
            birthday = res.birthday
            email = res.email
            group_id = res.group_id
            if sex == 'Male':
                sex = '男'
            elif sex == 'Female':
                sex = '女' 
            if group_id == 1:
                per = '管理员'
            elif group_id == 2:
                per = '普通用户'
        dic1 = {'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per,'page_number':1}
        #把对应的提示信息加入到dic1中
        dic1['message'] = message
        dic1['title'] = title
        dic1['style'] = style
        #查询朋友动态信息
        friends_info = FriendInfo.query.order_by(FriendInfo.create_time.desc()).limit(3)
        friends_info_list = []
        for i in friends_info:
            data = i.__dict__
            #评论信息ID
            comment_id = data['id']
            #print(comment_id)
            comments_info = FriendComments.query.filter_by(friendinfo_id = comment_id).order_by(FriendComments.commenting_time.desc()).limit(5)
            comments_list = []
            for j in comments_info:
                data_1 = j.__dict__
                #删除多余字段
                del data_1['_sa_instance_state']
                data_1['style'] = random.choice(['success','info','warning','error',''])
                comments_list.append(data_1)
            data['comments_list'] = comments_list
            #对data进行处理
            del data['_sa_instance_state']
            del data['picture_path']
            #处理时间time_format
            digital_week_dic = {'1':'星期一','2':'星期二','3':'星期三','4':'星期四','5':'星期五','6':'星期六','7':'星期日'}
            time_list = data['time_format'].split(',')
            data['week'] = digital_week_dic[ time_list[3]]
            data['date'] = time_list[0] +'年' +time_list[1] +'月' + time_list[2] +'日'
            friends_info_list.append(data)
        return render_template('blog_1.html',dic1 = dic1, form = form ,list1 = friends_info_list)

#朋友圈动态评论翻页
# @app.route('/my_friends/comments/nextpage',methods = ['GET'])
# @login_required
# #@routing_permission_check
# def my_friend_comments_nextpage():
#     form = MyFriendsSendMessageForms()
#     current_user = session.get('user_id')
#     if request.method == 'GET':
#         #定义字典渲染页面
#         page_number = request.args.get('page')
#         try:
#             page_number = int(page_number)
#         except:
#             return abort(404)
#         else:
#             res = User.query.filter_by(username = current_user).first()
#             if res:
#                 chinese_name = res.chinese_name
#                 sex = res.sex
#                 birthday = res.birthday
#                 email = res.email
#                 group_id = res.group_id
#                 if sex == 'Male':
#                     sex = '男'
#                 elif sex == 'Female':
#                     sex = '女' 
#                 if group_id == 1:
#                     per = '管理员'
#                 elif group_id == 2:
#                     per = '普通用户'
#             dic1 = {'current_user':current_user,'chinese_name':chinese_name,\
#                 'sex':sex,'birthday':birthday,'email':email,'permission':per,'page_number':page_number}
#             #查询朋友动态信息
#             #根据页码查询不同的数据
#             offset_num = (page_number-1)*3
#             limit_num = 3
#             friends_info = FriendInfo.query.order_by(FriendInfo.create_time.desc()).limit(limit_num).offset(offset_num)
#             friends_info_list = []
#             for i in friends_info:
#                 data = i.__dict__
#                 #评论信息ID
#                 comment_id = data['id']
#                 comments_info = FriendComments.query.filter_by(friendinfo_id = comment_id).order_by(FriendComments.commenting_time.desc()).limit(5)
#                 comments_list = []
#                 for j in comments_info:
#                     data_1 = j.__dict__
#                     #删除多余字段
#                     del data_1['_sa_instance_state']
#                     data_1['style'] = random.choice(['success','info','warning','error',''])
#                     comments_list.append(data_1)
#                 data['comments_list'] = comments_list
#                 #对data进行处理
#                 del data['_sa_instance_state']
#                 del data['picture_path']
#                 #处理时间time_format
#                 digital_week_dic = {'1':'星期一','2':'星期二','3':'星期三','4':'星期四','5':'星期五','6':'星期六','7':'星期日'}
#                 time_list = data['time_format'].split(',')
#                 data['week'] = digital_week_dic[ time_list[3]]
#                 data['date'] = time_list[0] +'年' +time_list[1] +'月' + time_list[2] +'日'
#                 friends_info_list.append(data)
#             return render_template('blog_1.html',dic1 = dic1, form = form ,list1 = friends_info_list)


#朋友圈点赞
@app.route('/my_friends/send_message/add_likes',methods = ['GET'])
@login_required
#@routing_permission_check
def my_friends_add_likes():
    current_user = session.get('user_id')
    if request.method == 'GET':
        friendinfo_id = request.args.get('friendinfo_id')
        try:
            friendinfo_id = int(friendinfo_id)
        except:
            return abort(404)
        else:
            try:
                #写入数据库
                db.session.add(FriendLikes(id = None,friendinfo_id = friendinfo_id ,\
                    like_user = current_user ,like_time = datetime.datetime.now()))
                #更新点赞数
                friends_info = FriendInfo.query.filter_by(id = friendinfo_id).first()
                if friends_info:
                    old_likes = friends_info.like_number
                    friends_info.like_number = old_likes + 1
                db.session.commit()
                flash('点赞成功!')
                return redirect('/my_friends')
            except:
                db.session.rollback()
                flash('点赞失败!数据库错误!')
                return redirect('/my_friends')
            finally:
                db.session.close()

#查看点赞列表
@app.route('/my_friends/send_message/get_likes_list',methods = ['GET'])
@login_required
#@routing_permission_check
def get_likes_list():
    pass

#删除评论(只能删除自己添加的评论或者动态作者可以删除该动态下的评论)
@app.route('/my_friends/send_message/delete_comments',methods = ['GET'])
@login_required
#@routing_permission_check
def my_friend_delete_comments():
    current_user = session.get('user_id')
    if request.method == 'GET':
        delete_id = request.args.get('id')
        if delete_id:
            try:
                delete_id = int(delete_id)
            except:
                return abort(404)
            else:
                #根据当前操作用户是否为评论发送者或者为动态作者
                #否则不执行删除操作
                #根据ID查发送者
                sender_info = FriendComments.query.filter_by(id = delete_id).first()
                if sender_info:
                    #发送者
                    sender = sender_info.commenting_user
                    #作者
                    author_info = FriendInfo.query.filter_by(id = sender_info.friendinfo_id).first()
                    if author_info:
                        author = author_info.send_user
                    else:
                        author = None
                else:
                    sender = None
                    author = None
                #判断
                if current_user == sender or current_user == author:
                    try:
                        db.session.delete(sender_info)
                        db.session.commit()
                        flash('删除成功! ')
                        return redirect('/my_friends')
                    except:
                        db.session.rollback()
                        flash('删除失败! 数据库错误!')
                        return redirect('/my_friends')
                    finally:
                        db.session.close()
                else:
                    flash('不是作者/评论用户 无权限删除该评论! ')
                    return redirect('/my_friends')
        else:
            return abort(404)      

#后台管理权限表管理主页
@app.route('/management/permissionTable',methods = ['POST','GET'])
@login_required
@routing_permission_check
def management_permission():
    #form = SearchPlantForms()
    current_user = session.get('user_id')
    if request.method == 'GET':
        #定义字典渲染页面
        res = User.query.filter_by(username = current_user).first()
        if res:
            chinese_name = res.chinese_name
            sex = res.sex
            birthday = res.birthday
            email = res.email
            group_id = res.group_id
            if sex == 'Male':
                sex = '男'
            elif sex == 'Female':
                sex = '女' 
            if group_id == 1:
                per = '管理员'
            elif group_id == 2:
                per = '普通用户'
        dic1 = {'current_user':current_user,'chinese_name':chinese_name,\
            'sex':sex,'birthday':birthday,'email':email,'permission':per}
        #查询权限数据(限制10条)
        permission_info = Permission.query.limit(10).all()
        if len(permission_info) ==0:
            permission_info_list=[]
        else:
            permission_info_list = []
            for i in permission_info:
                data = i.__dict__
                del data['_sa_instance_state']
                data['style'] = random.choice(['success','info','warning','error'])
                permission_info_list .append(data)              
        return render_template('management.html',dic1 = dic1,list1 = permission_info_list)


#后台管理用户表
@app.route('/management/userTable',methods = ['POST','GET'])
@login_required
#@routing_permission_check
def management_user():
    pass

#后台管理用户表
@app.route('/management/Table',methods = ['POST','GET'])
@login_required
#@routing_permission_check
def management_user1():
    pass

#后台管理用户组表

#后台管理设备表

#后台管理朋友圈动态表

#后台管理朋友圈动态评论表

#后台管理朋友圈评论点赞信息表


if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = 5001,debug = True)
