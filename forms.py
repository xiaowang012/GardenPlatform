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