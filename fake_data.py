import random
import os
from datetime import datetime
from main import create_app
# from main.models.admin import User
from extensions import user_datastore, set_password
from database import db

# Get the ENV from os environment
env = os.environ.get('LOAN_ENV', 'development')
# Create the app instance via Factory method
app = create_app(env.lower())

with app.app_context():
    db.create_all()
    # 创建普通用户角色和Admin角色
    user_role = user_datastore.find_or_create_role(name='User', description='Generic user role')
    admin_role = user_datastore.find_or_create_role(name='Admin', description='Admin user role')
    # 创建管理员
    if not user_datastore.get_user('root@abc.com'):
        admin = user_datastore.create_user(email='root@abc.com',
                                           username='root',
                                           password=set_password('root'))
        # 为admin添加Admin角色(admin_role)
        user_datastore.add_role_to_user(admin, admin_role)
    """
    if not user_datastore.get_user('94589040@qq.com'):
        admin = user_datastore.create_user(email='94589040@qq.com',
                                           name='wangjianjun',
                                           password=set_password('root'))
        user_datastore.add_role_to_user(admin, admin_role)

    if not user_datastore.get_user('99541130@qq.com'):
        admin = user_datastore.create_user(email='99541130@qq.com',
                                           name='yuanxu',
                                           password=set_password('root'))
        user_datastore.add_role_to_user(admin, admin_role)
    """
    db.session.commit()
