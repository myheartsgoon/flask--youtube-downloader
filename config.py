import os

# Flask app config
SQLALCHEMY_DATABASE_URI = os.environ['YT_DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'development-key'

# Send email config
MAIL_SERVER = 'smtp.qq.com'   # Mail server address
MAIL_PORT = 465   # Mail server port
MAIL_USE_TLS = False   # Disable TLS
MAIL_USE_SSL = True   # Enable SSL
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


# Convert config
options = {
    'quiet': '',
    'encoding': "UTF-8",
    }
PATH_wkthmltopdf = os.environ['PATH_PDF']