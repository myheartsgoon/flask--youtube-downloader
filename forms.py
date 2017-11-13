from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class GenerateForm(Form):
    youtube_url = StringField('Youtube URL', validators=[DataRequired('Please enter a youtube video URL')], render_kw={"placeholder": "Enter youtube url"})
    generate = SubmitField('Submit')


class SearchUserForm(Form):
    user_acct = StringField('User Account', validators=[DataRequired('Please enter a user account')], render_kw={"placeholder": "Enter youtube user to search"})
    get = SubmitField('Submit')


class DownloadForm(Form):
    quality = SelectField('Quality')
    download = SubmitField('Submit')


class ConvertForm(Form):
    web_url = StringField('Web URL', validators=[DataRequired('Please enter a valid web URL')], render_kw={"placeholder": "Enter url to convert"})
    convert = SubmitField('Convert')


class SearchVideoForm(Form):
    keyword = StringField('Video Keyword', validators=[DataRequired('Please enter a keyword for swarch')], render_kw={"placeholder": "Enter keyword to search"})
    search = SubmitField('Search')


class SignupForm(Form):
    first_name = StringField('First name', validators=[DataRequired('Please enter your first name')])
    last_name = StringField('Last name', validators=[DataRequired('Please enter your last name')])
    email = StringField('Email', validators=[DataRequired('Please enter your email address'), Email('Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter your password'), Length(min=6, message='Password must be at least 6 character')])
    submit = SubmitField('Sign up')


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired('Please enter your email address'), Email('Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter your password')])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in')