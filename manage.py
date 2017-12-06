from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from models import db, User, Youtube, Convert
from routes import app

manager = Manager(app)
migrate = Migrate(app, db)

# @Manager.command
# def runserver():
#     app.run('0.0.0.0', port=8080)

manager.add_command('runserver', Server(host='127.0.0.1', port=7345))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()