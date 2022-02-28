#coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SelectField,DateField,SubmitField,FileField,TextAreaField
from wtforms.fields.core import IntegerField
from wtforms.validators import AnyOf, DataRequired, EqualTo,Length, NumberRange
from flask_wtf.file import FileRequired,FileAllowed

#用户注册表单
class RegisterForms(FlaskForm):
    username = StringField('username',validators = [DataRequired('用户名不能为空!'),Length(min=6,max=12,message = '用户名长度必须为6-12!')])
    password = PasswordField ('password',validators = [DataRequired('密码不能为空!'),Length(min=6,max=12,message = '密码长度必须为6-12!')])
    password1 = PasswordField ('password1',validators = [DataRequired('密码1不能为空!'),Length(min=6,max=12,message = '密码长度必须为6-12!'),EqualTo('password',message = '两次密码输入不一致!')])
    chinese_name = StringField('chinese_name',validators = [DataRequired('姓名不能为空!'),Length(min=1,max=12,message = '姓名长度必须为1-12!')])
    sex = StringField('sex',validators = [DataRequired('性别不能为空!'),Length(min=1,max=12,message = '性别长度必须为1-12!')])
    birthday = StringField('birthday',validators = [DataRequired('生日不能为空!'),Length(min=1,max=12,message = '生日长度必须为1-12!')])
    email = StringField('email',validators = [DataRequired('邮箱不能为空!'),Length(min=1,max=20,message = '邮箱长度必须为1-20!')])
    submit = SubmitField('submit')

#用户修改密码表单
class UserUpdatePasswordForms(FlaskForm):
    username = StringField('username',validators = [DataRequired('用户名不能为空!'),Length(min=6,max=12,message = '用户名长度必须为6-12!')])
    old_password = PasswordField ('old_password',validators = [DataRequired('原密码不能为空!'),Length(min=6,max=12,message = '密码长度必须为6-12!')])
    new_password1 = PasswordField ('new_password1',validators = [DataRequired('新密码1不能为空!'),Length(min=6,max=12,message = '密码长度必须为6-12!')])
    new_password2 = PasswordField ('new_password2',validators = [DataRequired('新密码2不能为空!'),Length(min=6,max=12,message = '密码长度必须为6-12!'),EqualTo('new_password2',message = '两次密码输入不一致!')])
    submit = SubmitField('submit')

#用户登录表单
class UserForms(FlaskForm):
    username = StringField('username',validators = [DataRequired('用户名不能为空!'),Length(min=6,max=12,message = '用户名长度必须为6-12!')])
    password = PasswordField ('password',validators = [DataRequired('密码不能为空!'),Length(min=6,max=12,message = '密码长度必须为6-12!')])
    submit = SubmitField('submit')

#我的盆摘界面查询植物的表单
class SearchPlantForms(FlaskForm):
    plant_name= StringField('plant_name',validators = [DataRequired('输入不能为空!')])
    submit = SubmitField('submit')

#我的盆摘界面添加设备
class AddDeviceForms(FlaskForm):
    plant_name = StringField('plant_name',validators = [DataRequired('植物名称不能为空!'),Length(1,50,message = '植物名称长度必须为1-50!')])
    plant_type = StringField ('plant_type',validators=[DataRequired('植物类别不能为空!'),Length(1,50,message = '植物类别长度必须为1-50!')])
    suggest_watering_time = StringField ('suggest_watering_time',validators=[DataRequired('浇水周期不能为空!'),Length(1,50,message = '浇水周期长度必须为1-50!')])
    device_name = StringField ('device_name',validators=[DataRequired('绑定设备不能为空!'),Length(1,50,message = '绑定设备长度必须为1-50!')])
    switch_number = StringField ('switch_number',validators=[DataRequired('开关编号不能为空!'),Length(1,50,message = '开关编号长度必须为1-50!')])
    submit = SubmitField('submit')

#我的盆摘批量导入设备
class ImportDevicesForms(FlaskForm):
    file = FileField('file',validators = [FileRequired(message = '文件上传不能为空!'),FileAllowed(['xlsx','xls'],message = '只支持Excel文件!')])
    submit = SubmitField('submit')

#我的盆摘修改设备信息
class UpdateDevicesForms(FlaskForm):
    id1 = StringField('id1')
    plant_name1 = StringField('plant_name1',validators = [DataRequired('植物名称不能为空!'),Length(1,50,message = '植物名称长度必须为1-50!')])
    plant_type1 = StringField ('plant_type1',validators=[DataRequired('植物类别不能为空!'),Length(1,50,message = '植物类别长度必须为1-50!')])
    suggest_watering_time1 = StringField ('suggest_watering_time1',validators=[DataRequired('浇水周期不能为空!'),Length(1,50,message = '浇水周期长度必须为1-50!')])
    device_name1 = StringField ('device_name1',validators=[DataRequired('绑定设备不能为空!'),Length(1,50,message = '绑定设备长度必须为1-50!')])
    switch_number1 = StringField ('switch_number1',validators=[DataRequired('开关编号不能为空!'),Length(1,50,message = '开关编号长度必须为1-50!')])
    submit = SubmitField('submit')

# #我的盆摘浇水操作开始浇水
# class DevicesWaterOperationStartForms(FlaskForm):
#     id1 = StringField('id1',validators = [DataRequired('id不能为空!')])
#     submit = SubmitField('submit')

# #我的盆摘浇水操作停止浇水
# class DevicesWaterOperationEndForms(FlaskForm):
#     id2 = StringField('id2',validators = [DataRequired('id不能为空!')])
#     submit = SubmitField('submit')


#添加权限表单
class AddPermissionForms(FlaskForm):
    group_name = StringField('group_name',validators=[DataRequired('name cannot be empty!')])
    url = StringField('url',validators=[DataRequired('url cannot be empty!')])
    description = StringField('description',validators=[DataRequired('permission description cannot be empty!')])
    submit = SubmitField('submit')

#批量导入权限的表单
class UploadPermissionForms(FlaskForm):
    file1 = FileField('file1',validators = [FileRequired(message = 'File cannot be empty!'),FileAllowed(['xlsx','xls'],message = 'File format error (XLSX/XLS only)!')])
    submit = SubmitField('submit')