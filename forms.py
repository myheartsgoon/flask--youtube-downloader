from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class GenerateForm(FlaskForm):
    youtube_url = StringField('Youtube链接', validators=[DataRequired('请输入Youtube链接')], render_kw={"placeholder": "Youtube链接"})
    generate = SubmitField('提交')


class SearchUserForm(FlaskForm):
    user_acct = StringField('Youtube账号', validators=[DataRequired('请输入Youtube账号')], render_kw={"placeholder": "Youtube账号"})
    get = SubmitField('提交')


class DownloadForm(FlaskForm):
    quality = SelectField('画质')
    download = SubmitField('提交')


class ConvertForm(FlaskForm):
    web_url = StringField('网页链接', validators=[DataRequired('请输入有效的网页链接')], render_kw={"placeholder": "网页链接"})
    convert = SubmitField('转换')


class SearchVideoForm(FlaskForm):
    keyword = StringField('视频关键字', validators=[DataRequired('请输入视频关键字')], render_kw={"placeholder": "搜索关键字"})
    search = SubmitField('搜索')


class SignupForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired('请输入用户名'), Length(max=20, message='用户名最长为25位')],
                              render_kw={"placeholder": "用户名"})
    email = StringField('邮箱', validators=[DataRequired('请输入你的邮箱'), Email('请输入有效的邮箱')], render_kw={"placeholder": "邮箱地址"})
    password1 = PasswordField('密码', validators=[DataRequired('请输入密码'), Length(min=6, message='密码需至少为6位')],
                              render_kw={"placeholder": "登陆密码"})
    password2 = PasswordField('密码', validators=[DataRequired('请再次输入密码'), Length(min=6, message='密码需至少为6位')],
                              render_kw={"placeholder": "再次输入登录密码"})
    submit = SubmitField('注册')


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired('请输入你的邮箱'), Email('请输入有效的邮箱')], render_kw={"placeholder": "邮箱地址"})
    password = PasswordField('密码', validators=[DataRequired('请输入密码')], render_kw={"placeholder": "登录密码"})
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class OAuthForm(FlaskForm):
    password1 = PasswordField('密码', validators=[DataRequired('请输入密码'), Length(min=6, message='密码需至少为6位')],
                              render_kw={"placeholder": "登陆密码"})
    password2 = PasswordField('密码', validators=[DataRequired('请再次输入密码'), Length(min=6, message='密码需至少为6位')],
                              render_kw={"placeholder": "再次输入登录密码"})
    submit = SubmitField('设置')