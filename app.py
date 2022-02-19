#coding=utf-8
from flask import Flask,render_template,request,\
    url_for,redirect,session,Response,g,jsonify,abort
from forms import UserForms,RegisterForms,SearchPlantForms,AddDeviceForms,\
    ImportDevicesForms
from werkzeug.utils import secure_filename
from config import DataBaseConfig,Config
from models import User,Devices ,Permission,UserGroup
from decorator import login_required, \
    routing_permission_check,get_hash_value
import os
import time
from dbs import db
import random
import xlrd

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
@login_required
@app.route('/my_plant/search/type',methods = ['GET'])
def search_plant_page_type():
    form = SearchPlantForms()
    if request.method == 'GET':
        plant_type = request.args.get('plant_type')
        number = request.args.get('number')
        if plant_type:
            try:
                number = int(number)
            except:
                return abort(404)
            else:
                dic1 = {'active1':'','active2':'','active3':'',\
                'active4':'','active5':'','current_page_number':number,'type1':plant_type}
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
@login_required
@app.route('/my_plant/AddDevice',methods = ['POST'])
def add_devices():
    form = AddDeviceForms()
    username = session.get('user_id')
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
                db.session.add(Devices(id = None,user_name = username,plant_name = plant_name,plant_type = plant_type,\
                    status = None,last_watering_time = None,suggest_watering_time = suggest_watering_time,device_name = device_name,\
                        switch_number = switch_number,add_time = time.strftime('%Y-%m-%d %H:%M:%S')))
                db.session.commit()
                #渲染主页
                dic1 = {'active1':'active','active2':'','active3':'',\
                'active4':'','active5':'','current_page_number':1,\
                'title':' 成功! ','message':'导入成功!',\
                'style':'alert alert-success alert-dismissable'}
                #查询devices表中的所有数据
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
            except:
                db.session.rollback()
                #渲染主页
                dic1 = {'active1':'active','active2':'','active3':'',\
                'active4':'','active5':'','current_page_number':1,\
                'title':' 错误! ','message':'导入失败!',\
                'style':'alert alert-dismissable alert-danger'}
                #查询devices表中的所有数据
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
            finally:
                db.session.close()
        else:
            #未通过表单校验，将错误消息拿出来
            err_dic = form.errors
            err1 = ''
            for key,value in err_dic.items():
                err1 += value[0] +'   '
            #渲染主页
            dic1 = {'active1':'active','active2':'','active3':'',\
            'active4':'','active5':'','current_page_number':1,\
            'title':' 错误! ','message':err1,\
            'style':'alert alert-dismissable alert-danger'}
            #查询devices表中的所有数据
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

#我的盆摘页面批量导入设备
@login_required
@app.route('/my_plant/ImportDevices',methods = ['POST'])
def ImportDevices():
    form = ImportDevicesForms()
    username = session.get('user_id')
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
                        add_data_list.append(Devices(id = None,user_name = username,plant_name = plant_name,plant_type = plant_type,\
                                            status = None,last_watering_time = None,suggest_watering_time = suggest_watering_time,\
                                            device_name = device_name,switch_number = switch_number,add_time = time.strftime('%Y-%m-%d %H:%M:%S')))
                    #一次添加所有数据add_all
                    if len(add_data_list) != 0:
                        try:
                            db.session.add_all(add_data_list)
                            db.session.commit()
                        except:
                            db.session.rollback()
                            message = '导入失败! '
                            style = 'alert alert-dismissable alert-danger'
                            title = '错误!  ' 
                        else:
                            message = '导入成功! '
                            style = 'alert alert-success alert-dismissable'
                            title = '成功!  ' 
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
        dic1 = {'active1':'active','active2':'','active3':'',\
        'active4':'','active5':'','current_page_number':1}
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
        response = Response(sendfile(file_path), content_type='application/octet-stream')
        response.headers["Content-disposition"] = 'attachment; filename=%s' % file_name 
        return response
    else:  
        return jsonify({'code':404,'message':'Unable to find resources'})

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
