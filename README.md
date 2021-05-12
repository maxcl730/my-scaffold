# my-scaffold

# application (api+management) with Python-Flask
项目需要Python3.6版本，安装requirement中的包。

#数据库维护
  
  * python manage.py db init
  * python manage.py db migrate
  * python manage.py db upgrade

#维护多语言资源
  * pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
  * pybabel extract -F babel.cfg -k lazy_gettext -o flask_security.pot .
  * pybabel init -i messages.pot -d translations -l zh_Hans_CN
  * 编译生成的zh语言文件
  * pybabel compile -d translations
  
 
  * pybabel compile -d translations/ -i translations/zh_Hans_CN/LC_MESSAGES/messages.po -l zh_Hans_CN
  
#启动服务
sh start.sh

#停止服务
sh stop.sh
