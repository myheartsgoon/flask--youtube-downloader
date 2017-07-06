from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class DownloadForm(Form):
    youtube_url = StringField('Youtube URL', validators=[DataRequired('Please enter a youtube video URL')])
    download = SubmitField('Download')

class SearchUserForm(Form):
    user_acct = StringField('User Account', validators=[DataRequired('Please enter a user account')])
    get = SubmitField('Get videos')
