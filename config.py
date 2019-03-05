#coding:utf-8
import os

# Application配置
settings = {
	'debug':True,
    'xsrf_cookies':True,
    'autoreload':True,
	'static_path':os.path.join(os.path.dirname(__file__), 'static'),
	'template_path':os.path.join(os.path.dirname(__file__), 'template'),
	'cookie_secret':'nHmXU+d7T7aKn71vXRQbj1Ba/6/lL0fIvRqy6bl/mnQ='
}

#mysql配置
mysql_options = dict(
    host='127.0.0.1',
    database='ihome',
    user='root',
    password='mysql'
)

#redis配置
redis_options = dict(
    host='127.0.0.1',
    port=6379
)


log_level = 'debug'
log_file = os.path.join(os.path.dirname(__file__), 'logs/log')

#　密码加密密钥
passwd_hash_key = 'nGvpb/rjQk+q5rt/TYMMQXdWS1yHXkl2u9NWn3XmQkc='