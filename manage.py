# -*- coding: utf-8 -*-
import os
from functools import wraps
from flask_script import Manager, Server
from main import create_app
from database import db
from flask_migrate import Migrate, MigrateCommand
from main.models import admin, member  # , trial, homepage, image, wechat, notify
# from common.wechat import WXApp
# from jobs.launcher import RunJob
import sys
sys.path.append('./main')

# Get the ENV from os environment
env = os.environ.get('LOAN_ENV', 'development')
# Create the app instance via Factory method
app = create_app(env.lower())
# Init manager object via app object
manager = Manager(app)

# Create a new commands: server
# This command will be run the Flask development_env server
manager.add_command("server", Server(host=app.config['BIND'], port=app.config['PORT']))
Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)  # 创建数据库映射命令


@manager.command
def show_config():
    from pprint import pprint
    pprint(app.config)


@manager.shell
def make_shell_context():
    """Create a python CLI.
    return: Default import object
    type: 'Dict'
    """
    # 确保有导入 Flask app object，否则启动的 CLI 上下文中仍然没有 app 对象
    return dict(app=app,
                db=db,
                User=admin.User,
                Role=admin.Role,
                #Member=member.Member,
                #MemberAddress=member.MemberAddress,
                )


if __name__ == '__main__':
    #from waitress import serve
    #serve(app, listen=app.config['LISTEN'])
    manager.run()
