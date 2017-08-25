from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class GenerateForm(Form):
    youtube_url = StringField('Youtube URL', validators=[DataRequired('Please enter a youtube video URL')])
    generate = SubmitField('Submit')

class SearchUserForm(Form):
    user_acct = StringField('User Account', validators=[DataRequired('Please enter a user account')])
    get = SubmitField('Submit')

class DownloadForm(Form):
    quality = SelectField('Quality')
    download = SubmitField('Submit')

class ConvertForm(Form):
    web_url = StringField('Web URL', validators=[DataRequired('Please enter a valid web URL')])
    convert = SubmitField('Convert')