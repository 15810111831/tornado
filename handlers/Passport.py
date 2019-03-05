#coding:utf-8

import re
import logging
import hashlib
import config

from utils.response_code import RET
from utils.session import Session
from BaseHandler import BaseHandler
from utils.commons import required_login

class IndexHandler(BaseHandler):
	def get(self):
		self.write('Hello World')
		# self.render('index.html',houses=[])

class RegisterHandler(BaseHandler):
	def post(self):
		mobile = self.json_data.get('mobile')
		passwd = self.json_data.get('password')
		sms_code = self.json_data.get('phonecode')

		if not all([mobile, passwd, sms_code]):
			return self.write(dict(errorcode=RET.PARAMERR, errormsg='参数不完整'))

		if not re.match(r'^1[3456789]{1}\d{9}', mobile):
			return self.write(dict(errorcode=RET.DATAERR, errormsg='手机号格式错误'))

		#判断短信验证码是否正确
		try:
			real_sms_code = self.redis.get('sms_code_%s'%mobile)
		except Exception as e:
			logging(e)
			return self.write(dict(errorcode=RET.DBERR, errormsg='查询验证码错出'))

		if not real_sms_code:
			return self.write(dict(errorcode=RET.NODATA, errormsg='验证码已过期'))

		if real_sms_code != sms_code:
			return self.write(dict(errorcode=RET.DATAERR, errormsg='验证码错误'))

		try:
			self.redis.delete('sms_code_%s'%mobild)
		except Exception as e:
			logging.error(e)

		#　保存数据,同时判断手机号是否存在,　判断的依据使数据库中mobile字段的唯一约束
		password = hashlib.sha256(passwd+config.passwd_hash_key).hexdigest()
		sql = 'insert into ih_user_profile(up_name, up_mobile, up_passwd) value(%(name)s, %(mobile)s, %(passwd)s)'

		try:
			user_id = self.db.execute(sql, name=mobile, mobile=mobile, passwd=password)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errorcode=RET.DATAEXIST, errormsg='手机号已存在'))

		session = Session(self)
		session.data['user_id'] = user_id
		session.data['mobile'] = mobile
		session.data['name'] = mobile
		try:
			session.save()
		except Exception as e:
			logging.error(e)

		self.write(dict(errorcode=RET.OK, errormsg='注册成功'))


class LoginHandler(BaseHandler):
	def post(self):
		mobile = self.json_data.get('mobile')
		passwd = self.json_data.get('password')

		if not all([mobile, passwd]):
			return self.write(dict(errorcode=RET.PARAMERR, errormsg='参数错误'))

		if not re.match(r'1[3456789]{1}\d{9}', mobile):
			return self.write(dict(errorcode=RET.DATAERR, errormsg='手机号错误'))

		#　检查密码是否正确
		sql = 'select up_user_id, up_name, up_passwd from ih_user_profile where up_mobile=%(mobile)s'

		res = self.db.get(sql, mobile = mobile)

		password = hashlib.sha256(passwd+config.passwd_hash_key).hexdigest()
		print res['up_passwd']
		print password
		if res and res['up_passwd'] == password:
			print '帐号密码正确'
			#　生成session数据
			# 返回客户端
			try:
				self.session = Session(self)
				self.session.data['user_id'] = res['up_user_id']
				self.session.data['mobile'] = mobile
				self.session.data['name'] = res['up_name']
				self.session.save()
				print '保存成功'
			except Exception as e:
				logging.error(e)
			return self.write(dict(errorcode=RET.OK, errormsg='OK'))
		else:
			return self.write(dict(errorcode=RET.DATAERR, errormsg='手机号或密码错误'))

			
class LogoutHandler(BaseHandler):
	"""退出登录"""
	@required_login
	def get(self):
		#　清除session数据
		self.session.clear()
		self.write(dict(errorcode=RET.OK, errormsg='退出成功'))


class CheckLoginHandler(BaseHandler):
	def get(self):
		if self.get_current_user():
			self.write({'errorcode':RET.OK, 'errormsg':'true', 'data':{'name':self.session.data['name']}})
		else:
			self.write({'errorcode':RET.SESSIONERR, 'errormsg':'false'})