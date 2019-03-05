#coding:utf-8

import logging
import constants

from .BaseHandler import BaseHandler
from utils.response_code import RET
from utils.commons import required_login
from utils.qiniu_storage import storage


class AvatarHandler(BaseHandler):
	"""上传头像"""
	@required_login
	def post(self):
		files = self.request.files.get('avatar')
		if not files:
			return self.write(dict(errorcode=RET.PARAMERR, errormsg='未传图片'))

		image_data = files[0]['body']
		try:
			image_name = storage(image_data)
		except EXcetion as e:
			logging.error(e)
			image_name = None
			
		if not image_name:
			return self.write(dict(errorcode=RET.THIRDERR, errormsg='上传失败'))

		user_id = self.session.data['user_id']
		sql = 'update ih_user_profile set up_avatar=%s where up_user_id=%s'
		try:
			ret = self.db.execute(sql, image_name, user_id)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errorcode=RET.DBERR, errormsg='upload failed'))

		image_url = constants.QINIU_URL_PREFIX + image_name
		self.write({'errorcode':RET.OK, 'errormsg':'OK', 'url':image_url})


class ProfileHandler(BaseHandler):
	"""个人信息"""
	@required_login
	def get(self):
		user_id = self.session.data['user_id']
		sql = 'select up_name, up_mobile, up_avatar from ih_user_profile where up_user_id=%(user_id)s'
		try:
			ret = self.db.get(sql,user_id=user_id)
		except Exception as e:
			logging.error(e)
			return self.write(dict(errorcode=RET.DATAERR, errormsg='get data err'))

		if ret['up_avatar']:
			image_url = constants.QINIU_URL_PREFIX + ret['up_avatar']
		else:
			image_url = None

		print image_url
		self.write({'errorcode':RET.OK, 'errormsg':'OK', 
		           'data':{'user_id':user_id, 'mobile':ret['up_mobile'], 'name':ret['up_name'], 'avatar':image_url
		           }})


class NameHandler(BaseHandler):
	"""修改用户名"""
	@required_login
	def post(self):
		user_id = self.session.data['user_id']
		name = self.json_data.get('name')

		if not name:
			return self.write(dict(errorcode=RET.PARAMERR, errormsg='参数错误'))

		#　保存昵称,并同时判断name是否重复(利用数据库唯一索引)
		try:
			sql = 'update ih_user_profile set up_name=%s where up_user_id=%s'
			self.db.execute_rowcount(sql, name, user_id)
		except Exception as e:
			logging.error(e)
			return self.write({'errorcode':RET.DBERR, 'errormsg':'name has exist'})

		#　修改session中name的字段,并保存到redis中
		self.session.data['name'] = name
		try:
			self.session.save()
		except Exception as e:
			logging.error(e)
		self.write({'errorcode':RET.OK, 'errormsg':'OK'})


class AuthHandler(BaseHandler):
	"""用户认证"""
	@required_login
	def post(self):
		user_id = self.session.data['user_id']
		real_name = self.json_data.get('real_name')
		id_card = self.json_data.get('id_card')
		if not real_name or not id_card:
			return self.write({'errorcode':RET.PARAMERR, 'errormsg':'参数错误'})

		try:
			sql = 'update ih_user_profile set up_real_name=%s,up_id_card=%s where up_user_id=%s'
			self.db.execute_rowcount(sql, real_name, id_card, user_id)
		except Exception as e:
			logging.error(e)
			return self.write({'errorcode':RET.DBERR, 'errormsg':'update failed'})

		self.write({'errorcode':RET.OK, 'errormsg':'OK'})

	@required_login
	def get(self):
		user_id = self.session.data['user_id']
		#从数据库中查找认证信息
		try:
			sql = 'select up_real_name, up_id_card from ih_user_profile where up_user_id=%s'
			ret = self.db.get(sql, user_id)
		except Exception as e:
			logging.error(e)
			return self.write({'errorcode':RET.DBERR, 'errormsg':'get data error'})

		if not ret:
			return self.write({'errorcode':RET.NODATA, 'errormsg':'no auth data'})

		self.write({'errorcode':RET.OK, 'errormsg':'OK', 'data':{'real_name':ret.get('up_real_name', ''), 'id_card':ret.get('up_id_card','')}})